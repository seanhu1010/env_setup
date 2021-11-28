# -*- coding: UTF-8 -*-
import os
import time
import stat
import select
from datetime import datetime
from envlib.env.envlogging import logger
import paramiko
from paramiko.ssh_exception import SSHException, AuthenticationException

__all__ = ['Ssh', ]


class Ssh(object):
    """ssh工具类，提供交互式ssh远程执行命令功能和sftp上传下载功能

    Attributes:
        host: str: 主机ip, 如'1.1.1.1'
        username: ssh登录用户名
        password: ssh登录密码
        port: int: ssh端口号，默认为22
    """

    DEFAULT_SSH_TIMEOUT = 20
    kubelet_prompt = r"/ #"

    def __init__(self, host=None, username=None, password=None, port=22):
        self.host = None
        self.username = None
        self.chan = None
        self.transport = None
        self.prompt = None
        self.ssh = None
        self.sftp_client = None
        self.sftp = None
        self.logger = logger

        if host and username and password:
            self.connect(host, username, password, port)

    def connect(self, host, username, password, port=22):
        """建立ssh连接

        Args:
            host: 主机地址
            username: 登录用户名
            password: 登录密码
            port: 登录端口,默认值：22

        Returns:
            None
        """

        try:
            self.host = host
            self.username = username
            if not self.ssh:
                self.ssh = paramiko.SSHClient()
                self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh.connect(hostname=host, username=username, password=password)

            self.prompt = r"]#" if username == "root" else r"]$"
            self.chan = self.ssh.invoke_shell('', width=999, height=999)
            self.chan.settimeout(60)  # DEFAULT_SSH_CHAN_TIMEOUT = 60

            self.sftp_client = paramiko.Transport((host, port))
            self.sftp_client.connect(username=username, password=password)
            self.sftp = paramiko.SFTPClient.from_transport(self.sftp_client)
            self.logger.debug("连接主机{}成功，使用用户名：{}".format(host, username))
        except AuthenticationException as ae:
            self.logger.error("连接主机{}鉴权错误，使用用户名：{}，密码：{}".format(host, username, password))
        except SSHException as se:
            self.logger.error("连接主机{}发生错误".format(host))

    def close(self):
        """关闭ssh连接"""
        try:
            if self.ssh:
                self.ssh.close()
            if self.sftp_client:
                self.sftp_client.close()
            self.logger.debug("ssh&sftp通道已关闭")
        except:
            pass

    def exec_cmd_and_return(self, cmd, timeout=DEFAULT_SSH_TIMEOUT):
        """执行带返回的命令并获取输出

        Args:
            cmd: 命令内容
            timeout: int,超时时间,默认值:20min

        Returns:
            stdout: cmd执行打印输出
            stderr: ?
        """

        _, stdout, stderr = self.ssh.exec_command(cmd, timeout=timeout)
        stdout = stdout.read().decode("utf-8", 'ignore').strip()
        stderr = stderr.read().decode("utf-8", 'ignore').strip()
        self.logger.debug("在主机:{}执行命令成功，命令内容:{}，执行用户:{}".format(self.host, cmd, self.username))
        self.logger.debug(stdout)
        return stdout, stderr

    def exec_cmds_with_expect(self, commands, timeout=60):
        """交互式执行命令行

        Args:
            commands: list of tuple,命令list
            timeout: int, 默认60min

        Returns:
            Output string

        Examples:
            Usage::

                Commands format: （命令，预期）
                [('ssh 1.1.1.1', '(yes/no)'),
                ('yes', 'Password:'),
                ('password', '#')]
        """

        out = self.chan.recv(1024).decode("utf-8", 'ignore')
        for cmd, expect in commands:

            self.chan.send(cmd + '\n')
            start = datetime.now()
            tout = ""
            while (datetime.now() - start).seconds < timeout:
                if self.chan.recv_ready():
                    cout = self.chan.recv(1024 * 10).replace(b"\r\r\n", b"\r\n")
                    tout += (cout.decode("utf-8", 'ignore'))

                    if tout.find(expect) > -1:
                        break
                time.sleep(0.5)
            else:
                raise Exception(
                    "Expect '%s' timeout(%ss) while Send '%s':\n%s" %
                    (expect, timeout, cmd, out))
            self.logger.debug("在主机:{}执行命令成功，命令内容:{}，执行用户:{}".format(self.host, cmd, self.username))
            out += tout
        self.logger.debug(out)
        return out

    def exec_cmd_with_stream(self, cmd, timeout=DEFAULT_SSH_TIMEOUT):
        """执行持续输出流的命令（例如kubectl logs -f）并获取输出

        Args:
            cmd: 命令内容
            timeout: int，超时时间，此处必须设置，否则命令无法退出, 默认20min

        Returns:
            cout: 输出

        Tips:
            kubectl命令通过paramiko执行时会报找不到命令，需在主机执行ln -s /root/local/bin/kubectl /usr/bin/kubectl以让系统识别到
        """

        sin, sout, serr = self.ssh.exec_command(cmd)

        def line_buffered(f):
            line_buf = ""

            while not f.channel.exit_status_ready():
                readq, _, _ = select.select([f.channel], [], [], timeout)
                line_buf += f.read(len(readq[0].in_buffer)).decode("utf-8", 'ignore')
                if line_buf.find('\n') > -1:
                    yield line_buf
                    line_buf = ''

        cout = ""
        start_time = datetime.now()
        for line in line_buffered(sout):
            if (datetime.now() - start_time).seconds < timeout:
                cout += line
            else:
                break

        self.logger.debug("在主机:{}执行命令成功，命令内容:{}，执行用户:{}".format(self.host, cmd, self.username))
        self.logger.debug(cout)
        return cout

    def get(self, remote_path, local_path):
        """从远端下载文件和目录到本地

        Args:
            remote_path: 本地目录或文件路径
            local_path: 远端目录或文件路径

        Returns:
            None

        Tips:
            1、远端路径为目录，本地路径为文件时会报错
            2、远端路径为目录时，默认是把远端目录下的文件（包括子文件夹）拷贝到本地，而远端目录本身并不会拷贝，请自行处理顶级目录
        """

        if not os.path.exists(local_path):
            os.makedirs(local_path)

        if os.path.isdir(local_path):
            try:
                self.sftp.listdir_attr(remote_path)
                self.logger.debug("远端路径是目录")
                self.get_directory(remote_path, local_path)
            except IOError as ioe:
                remote_filename = remote_path.split("/")[-1]
                local_filename = os.path.join(local_path, remote_filename)
                self.logger.debug("拷贝远端文件:{} 到本地:{}".format(remote_path, local_filename))
                self.get_file(remote_path, local_filename)
        else:
            try:
                self.sftp.listdir_attr(remote_path)
                self.logger.error("不能把远端目录复制到本地文件")
            except IOError as ioe:
                self.get_file(local_path, remote_path)

    def put(self, local_path, remote_path):
        """从本地上传文件和目录到远端

        Args:
            local_path: 本地目录或文件路径
            remote_path: 远端目录或文件路径

        Returns:
            None

        Tips:
            1、本地路径为目录，本远端路径为文件时会报错
            2、本地路径为目录时，默认是把本地目录下的文件（包括子文件夹）拷贝到远端，而本地目录本身并不会拷贝，请自行处理顶级目录
        """

        if os.path.isdir(local_path):
            try:
                self.sftp.listdir_attr(remote_path)
                self.logger.debug("上传本地文件夹:{}, 到远端文件夹:{}".format(local_path, remote_path))
                self.put_directory(local_path, remote_path)
            except IOError as ioe:
                self.logger.error("不能把本地目录上传到远端文件")
                self.logger.error(ioe)
        else:
            try:
                self.sftp.listdir_attr(remote_path)
                local_filename = os.path.split(local_path)[-1]
                if remote_path[-1] == "/":
                    remote_filename = remote_path + local_filename
                else:
                    remote_filename = remote_path + "/" + local_filename
                self.logger.debug("上传本地文件:{}, 到远端文件夹:{}".format(local_path, remote_path))
                self.put_file(local_path, remote_filename)
            except IOError as ioe:
                self.logger.debug("上传本地文件:{}, 到远端文件:{}".format(local_path, remote_path))
                self.put_file(local_path, remote_path)

    def get_file(self, remote_path, local_path):
        """从远端下载文件到本地

        Args:
            remote_path: 本地文件路径
            local_path: 远端文件路径

        Returns:
            None
        """

        self.sftp.get(remote_path, local_path)

    def get_directory(self, remote_path, local_path):
        """从远端下载目录到本地

        Args:
            remote_path: 本地目录路径
            local_path: 远端目录路径

        Returns:
            None
        """

        # 获取远端linux主机上指定目录及其子目录下的所有文件
        try:
            # listdir_attr方法会抛出异常，需手动接收一下，不然被外层except捕获会导致目录被当成问价来复制
            for a in self.sftp.listdir_attr(remote_path):
                r = remote_path.rstrip("/") + "/" + a.filename
                l = os.path.join(local_path, a.filename)
                if stat.S_ISDIR(a.st_mode):
                    if not os.path.exists(l):
                        os.makedirs(l)
                    self.logger.debug("递归拷贝子目录:{},到本地:{}".format(r, l))
                    self.get_directory(r, l)
                else:
                    self.logger.debug("拷贝远端文件:{}, 到本地文件:{}".format(remote_path, local_path))
                    self.sftp.get(r, l)
        except IOError as ioe:
            pass

    def put_file(self, local_path, remote_path):
        """从本地上传文件到远端

        Args:
            local_path: 本地文件路径
            remote_path: 远端文件路径

        Returns:
            None
        """

        self.logger.debug("拷贝本地文件:{}, 到远端文件:{}".format(remote_path, local_path))
        self.sftp.put(local_path, remote_path)

    def put_directory(self, local_dir, remote_dir):
        """从本地上传目录到远端

        Args:
            local_dir: 本地目录路径
            remote_dir: 远端目录路径

        Returns:
            None
        """

        try:
            start_upload = datetime.now()
            self.logger.debug("开始上传本地文件夹:{}".format(local_dir))
            for root, dirs, files in os.walk(local_dir):
                for file in files:
                    local_file = os.path.join(root, file)
                    a = local_file.replace(local_dir, '')
                    relative_path = "/".join(a.strip(os.sep).split(os.sep))
                    remote_file = remote_dir.rstrip("/") + "/" + relative_path
                    try:
                        self.sftp.put(local_file, remote_file)
                    except IOError as e:
                        self.sftp.mkdir(os.path.split(remote_file)[0])
                        self.sftp.put(local_file, remote_file)
                        self.logger.debug("拷贝本地文件:{}, 到远端文件:{}".format(local_file, remote_file))
                for name in dirs:
                    local_path = os.path.join(root, name)
                    a = local_path.replace(local_dir, '')
                    relative_path = "/".join(a.strip(os.sep).split(os.sep))
                    remote_path = remote_dir.rstrip("/") + "/" + relative_path
                    try:
                        self.sftp.mkdir(remote_path)
                        self.logger.debug("创建远端文件夹:{}".format(remote_path))
                    except Exception as e:
                        self.logger.debug(e)

            upload_spend = (datetime.now() - start_upload).seconds
            self.logger.debug('上传成功，总时长：{}秒'.format(upload_spend))

        except Exception as e:
            self.logger.debug("上传时发生了错误")
            self.logger.error(e)

    def get_host_date_rest(self, before=0):
        """获取主机时间，作为接口入参，时间格式为2019-06-12 10:26:53

        Args:
            before: int 向前推移时间，单位为天, 默认不推移，即获取当前时间

        Returns:
            str: 主机时间
        """

        sh = f'date -d "-{before} day" "+%Y-%m-%d %H:%M:%S"'
        ret = self.exec_cmd_and_return(sh)
        return ret[0]

    def get_host_date_rfc3339(self, before=0):
        """获取主机rfc3339格式时间，用于pod日志查询时指定时间点查询对应时间点以后的日志

        Args:
            before: 向前倒推时间，默认0s，可以避免日志查询时失败

        Returns:
            主机rfc3339格式时间
        """

        ret = self.exec_cmd_and_return("date --rfc-3339=seconds")
        if before != 0:
            time_split = ret[0].split('+')
            time_tamp = time.mktime(time.strptime(time_split[0], "%Y-%m-%d %H:%M:%S"))
            time_tamp -= before
            local = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time_tamp))
            re_time = local.replace(' ', 'T') + '+' + time_split[1]
        else:
            re_time = ret[0].replace(' ', 'T')

        return re_time

    def get_host_date_stamp(self, accuracy='ms'):
        """获取主机时间戳格式时间

        Args:
            accuracy: 精度，取值：'ms', 's', 默认精度为'ms'，返回13位整数

        Returns:
            int: 主机时间戳格式时间
        """

        s_str = self.exec_cmd_and_return("date +%s")[0]
        if accuracy == 'ms':
            ns_str = self.exec_cmd_and_return("date +%N")[0]
            return int(s_str + ns_str[:3])
        elif accuracy == 's':
            return int(s_str)

    def get_time_quantum_stamp(self, before, after, now=None, accuracy='ms'):
        """通过当前时间点加偏移量获取时间段的两个时间戳

        Args:
            before: 向前偏移量，格式：1（秒,不带单位），1m（分），1h（时），1d（天），1w（周），偏移量不支持ms
            after: 向后偏移量
            now: 当前时间，时间戳格式，默认为None，调用get_host_date_stamp获取
            accuracy: 精度，取值：'ms', 's', 默认为ms

        Returns:
            (start_time, end_time)
        """

        now = int(now) if now else self.get_host_date_stamp(accuracy)
        before = int(before) if before[-1].isdigit() else self.convert_to_seconds(before)
        after = int(after) if after[-1].isdigit() else self.convert_to_seconds(after)

        if accuracy == 'ms':
            start_time = now - before * 1000
            end_time = now + after * 1000
        elif accuracy == 's':
            start_time = now - before
            end_time = now + after
        else:
            raise ValueError("Param 'accuracy' just support 'ms' or 's'.")

        return start_time, end_time

    def get_time(self, time_unit="hour", start_to_now=0, time_type="%s", stamp13=False):
        """
        获取服务器的时间戳或时间格式
        :create: yinjia@2021.02.07

        Args:
            start_to_now: 时间偏移量，负数表示当前时间前多少（小时等）时间，正数表示未来的时间，不支持小数
            time_unit: 时间单位，year, month，day, hour, minute, second等
            time_type: 时间格式，默认为%s（时间戳）；其他时间格式，例如：%Y-%m-%d %H:%M:%S
            stamp13: bool: False10位时间戳 True13位时间戳

        Returns:
            time
        """
        time_unit = time_unit.split("s")[0]

        sh = f'date -d "{int(start_to_now)} {time_unit}" "+{time_type}"'
        ret, _ = self.exec_cmd_and_return(sh)

        # self.close()

        if time_type == "%s":
            if stamp13:
                return int(ret) * 1000
            else:
                return int(ret)
        else:
            return ret

    def get_start_and_end_time(self, start, times, time_unit, time_type="%s", stamp13=False):
        """
        获取服务器start和end时间戳或时间格式
        :create: yinjia@2021.02.07

        Args:
            start: 开始时间偏移量，负数表示当前时间前多少（小时等）时间，正数表示未来的时间，不支持小数
            times: 总时间区间长度
            time_unit: 时间单位，year, month，day, hour, minute, second等
            time_type: 时间格式，默认为%s时间戳；其他时间格式，例如：%Y-%m-%d %H:%M:%S
            stamp13: bool: False10位时间戳 True13位时间戳

        Returns:
            start, end
        """

        time_unit = time_unit.split("s")[0]

        sh_now = f'date -d "{int(start)} {time_unit}" "+%Y%m%d %H:%M:%S"'
        t, _ = self.exec_cmd_and_return(sh_now)
        sh_start = f'date -d "{t}" "+{time_type}"'
        start, _ = self.exec_cmd_and_return(sh_start)
        sh_end = f'date -d "{t} {int(times)} {time_unit}" "+{time_type}"'
        end, _ = self.exec_cmd_and_return(sh_end)

        # self.close()

        if time_type == "%s":
            if stamp13:
                return int(start) * 1000, int(end) * 1000
            else:
                return int(start), int(end)
        else:
            return start, end

    @staticmethod
    def convert_to_seconds(s):
        """将时间描述字符串转换为秒数

        Args:
            s: 格式：1m（分），1h（时），1d（天），1w（周）

        Returns:
            second
        """

        seconds_per_unit = {"m": 60, "h": 3600, "d": 86400, "w": 604800}

        return int(s[:-1]) * seconds_per_unit[s[-1]]

    def get_pod_log(self, pod_name, since_time=None, since=None, greps=None, grep_abc=None):
        """获取pod日志

        Args:
            pod_name: pod名，前缀，自动匹配
            since_time: 日志过滤条件--since-time，rfc3339格式，过滤该时点后的所有日志，eg, 2019-03-01T04:30:13.000+08:00
            since: 日志过滤条件--since，过滤当前时间前到之前since时长的日志，eg, 5s，2m，3h
            greps: 日志过滤条件，grep eg: ``['1', '2'] -> |grep '1' |grep '2'``
            grep_abc: grep过滤参数，eg: ``{'-A': 1, '-B': 2, '-C': 3}``

        Returns:
            log 查询回显
        """

        if 'vias' in pod_name.lower():
            self.logger.warning("Not support vias pod")
            return ''

        greps = greps if greps else list()
        grep_abc = grep_abc if grep_abc else dict()

        # 生成命令grep过滤条件，eg：-A 1 -B 2
        grep_abc_str = str()
        for j in grep_abc.keys():
            grep_abc_str += ' {} {}'.format(j, str(grep_abc[j]))

        # 生成命令grep字符串
        grep_str = str()
        for grep in greps:
            grep_str += ' |grep \'{}\''.format(grep)
        grep_str += grep_abc_str
        self.logger.info("The command param of grep is '{}'".format(grep_str))

        cmd = "kubectl logs $(kubectl get pod|grep {}|awk '{{print $1}}')".format(pod_name)

        # --since-time与--since不可同时存在
        if since_time:
            cmd += ' --since-time={}'.format(since_time)
        elif since:
            cmd += ' --since={}'.format(since)

        cmd += grep_str
        self.logger.info("The command is: '{}'".format(cmd))
        logs, _ = self.exec_cmd_and_return(cmd)
        self.logger.info("Get logs complete: '{}'".format(logs))

        return logs

    def exec_cmd(self, cmd, expect=None, timeout=3):
        """
        cmd持续交互，继承上一条命令的界面
        :param cmd:
        :param timeout: Timeout.
        :param expect:
        :return: Output string.
        """

        self.chan.send(cmd + '\n')
        start = datetime.now()
        tout = ""
        while (datetime.now() - start).seconds < timeout:
            if self.chan.recv_ready():
                out = self.chan.recv(1024 * 10).replace(b"\r\r\n", b"\r\n")
                tout += (out.decode("utf-8", 'ignore'))
            if expect and (tout.find(expect) > -1):
                break
            time.sleep(0.5)
        self.logger.debug("在主机:{}执行命令成功，命令内容:{}，执行用户:{}".format(self.host, cmd, self.username))
        self.logger.debug(tout)
        return tout


if __name__ == '__main__':
    pass

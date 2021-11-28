Introduction
=============

# 1. 项目简介


预置驱动库框架，提供一些基础的预置库方法，方便进行端到端自动化预置，工程地址


基于 [pytest](https://docs.pytest.org/en/6.2.x/) 测试框架 + [allure](https://docs.qameta.io/allure/) 生成测试报告


### **目标**


* 方便实现端到端自动化及类生产性能测试


### **主要亮点**

* 分层设计
  
* 全局代理模式，上下文堆栈(with触发)
  
* 采用过程存储方式将端到到操作过程中产生的中间数据缓存在`g` 变量中，`g` 变量支持 `k-v` 形式的快捷数据提取，供后续接口调用

* 支持多用户/多环境并行处理

* 支持根据模板生成api函数方法


#### level定义:

* level0: 如服务状态检查`K8s`,存储状态查询`Storage`,综合管理`Uuv`,各类tool`Kafka`等

* level1: cms配置`Cms`,vms配置`Vms`等

* level2: 对象管理`Object`,设备资源管理`Udm`等

* level3: 解析`FullAnalysis`,布控`MDisposition`等


# 2. 主要库

* **database**: 数据库连接操作

* **id_info**: 身份信息生成

* **rest**: restful接口操作基础库

* **smb**: SMB轻量连接与操作, 用于远端访问共享目录, 分离二进制文件

* **threadings**: *试验*多线程模块

* **ssh**: ssh工具类，提供交互式ssh远程执行命令功能和sftp上传下载功能

* **util**: 工具库，提供随机数，Md5，等方法

* **env**: 借鉴flask实现了基于代理模式的预置驱动app,

* **envsetup**: 预置驱动库，提供一些易于使用的类方法，如K8s, Cms, Storage, Vms, Uuv, Object, Udm, etc.

* **env_resources**: 预置驱动库数据


### **驱动库的一般准则**

#### 1）绑定绝大多数发生在query函数, 可以使用模块名.get_keys获取绑定值列表，如

    Uuv.get_keys()
    {'uuv_department_list': '函数名: query_uuv_department_by_rest, 含义: '
                            '传入params，查询部门信息',
     'uuv_organization_list': '函数名: query_uuv_organization_by_rest, 含义: '
                              '传入params，查询组织list'}

#### 2）绑定的值和函数的返回值保持一致，允许对res的进行加工，如以下函数bind_to_g中绑定的value与return应一致

    @classmethod
    def query_uuv_organization_by_rest(cls, check=False, **kwargs):
        """传入params，查询组织list"""
        params = {'type': 0, 'page_index': 1, 'page_size': 200}
        params.update(**kwargs)
        res = app.send_by_rest('/api/demo@get', params=params, check=check)
        app.bind_to_g(key='uuv_organization_list', value=res.get('data'), lock=False)
        return res.get('data')

#### 3）key命名方式:

绑定的key以 “类名_key实际含义_数据类型”进行命名，value数据类型为字典时，数据类型可省略，如cms_archive_config

#### 4）函数命名方式:

统一使用 “操作 + 函数实际作用 + 方式 + 方法 + [via_条件]/[from_配置文件]” 的格式来作为函数名称, 


其中“操作”可用字段：

* 添加：create

* 删除：delete

* 修改：modify

* 查询：query

* 配置: config

* 操作：do

* 校验: check

* 可选副词批量处理: batch
      
“函数实际作用”

“方式”可用字段：

* 通过：by

* 伴随数据：with
      
“方法”可用字段：

* 日志：log

* 接口：rest

* 界面：web

* 抓包：patch

* 数据库：database

* 远程共享目录：smb
      
”可选“，[via_条件]/[from_配置文件]

条件可用字段：

* 单个条件：something

* 多个条件：kw

* json体：json

* data体：data

##### **示例**

    通过rest方法，传入单个条件org_name,查询组织下编码器通道列表
    query_encoder_channel_list_by_rest_via_org_name

    通过rest方法，传入json体，检索对象管理-人员列表
    query_person_manage_person_list_via_json

    通过rest方法，传入多个参数，新建分组
    add_object_group_by_rest_via_kw

#### 5）区分函数是否可直接调用：

不含via及含单个条件如(query_encoder_channel_list_by_rest_via_org_name)的函数能直接调用;
含多个条件via_kw, 及传入特定数据via_json, via_data, via_params的函数不推荐直接调用

### Docstrings
推荐使用[Google style](https://google.github.io/styleguide/pyguide.html#s3.8-comments-and-docstrings), PyCharm->Settings->Tools->Docstrings->Docstrings format选择Google, All of the following section headers are supported:

* Args (alias of Parameters)
* Arguments (alias of Parameters)
* Attention
* Attributes
* Caution
* Danger
* Error
* Example
* Examples
* Hint
* Important
* Keyword Args (alias of Keyword Arguments)
* Keyword Arguments
* Methods
* Note
* Notes
* Other Parameters
* Parameters
* Return (alias of Returns)
* Returns
* Raise (alias of Raises)
* Raises
* References
* See Also
* Tip
* Todo
* Warning
* Warnings (alias of Warning)
* Warn (alias of Warns)
* Warns
* Yield (alias of Yields)
* Yields

# 3. 提交说明

### 分支

* master分支为主分支（保护分支），不能直接在master上进行修改代码提交

* develop分支为测试分支，所有开发完成需要提交测试的功能合并到该分支

* feature分支为开发分支，大家根据不同需求创建独立的功能分支，开发完成后合并到develop分支

* fix分支为bug修复分支，需要根据实际情况对已发布的版本进行漏洞修复时使用该分支

### 审核制度
略

### Tag

采用三段式， v版本.里程碑.序号，如 v1.2.1

* 架构升级或架构重大调整，修改第1位

* 新功能上线或者模块大的调整，修改第2位

* bug修复上线，修改第3位

### Git提交信息

Commit Message一般包含三部分：Header，Body和Footer

#### Header


* type：用于说明commit的类别，规定为如下几种

* feat：新增功能；

* fix：bug修复；

* docs：修改文档；

* refactor：代码重构，未新增任何功能和修复bug；

* build：改变构建流程，新增依赖库，工具等；

* style：仅仅修改了空格、缩进等，不改变代码逻辑；

* perf：改善性能和体现的修改；

* chore：非src和test的修改；

* test：测试用例的修改；

* ci：自动化流程配置修改；

* revert：回滚到某个版本；

* scope：【可选】用于说明commit的影响范围

* subject：commit的简短说明，尽量简短

#### Body

* 本次commit的详细描述，可分多行

##### Footer

* 不兼容变动：需要描述相关信息；

* 关闭指定的Issue：输入Issue信息；

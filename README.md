# client_manager
之前产品给策划用的pc版本管理工具，用于快速下载版本使用（项目流程改动后，工具即废弃）

原有的流程为unity或其他工程导出PC用的测试客户端exe文件和资源文件夹，所有的内容会存储到ftp机器进行备份，并分版本号文件夹管理
所以，为快速链接和获取所需版本，制作的工具

之后的流程变动，取消了PC版本打包exe，直接使用unity工程预览，同时，通过jenkins的持续应用，大幅优化了android、ios打包、发布的流程，这个工具后面改成了基于web网页的备份、发布、安装平台了，代码详见github的另外一个仓库

这里仅作为代码纪念，以及避免以后需要查找所用
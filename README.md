![](https://s2.loli.net/2022/11/19/6KapmFyEdcWjNwf.png)

# 《僵尸毁灭工程》41.78版小工具：绘制地图模组所在区域指示图

## 功能特性

绘制《僵尸毁灭工程》41.78版某个沙盒模式存档使用的模组地图所在的区块。

- 使用不同的颜色区分不同模组。
- 用红色高亮相互重叠的模组区域，并用黄色字体显示重叠的模组。



## 安装和使用

### 0. 系统要求

1. 适用于Windows系统。未对Linux系统测试。
2. 仅适用于基于原版肯塔基州地图的存档。已对沙盒模式进行测试。不适用于基于Cherbourg等替换原版地图的模组的存档。



### 1. 安装

1. 下载全部文件。请确保下载完成后仍预留至少100M的磁盘空间。

2. 安装Python。请使用Python3。

3. 安装`Pillow`包。可在命令提示符中输入以下代码：

    ```
    python3 -m pip install --upgrade pip
    python3 -m pip install --upgrade Pillow
    ```



### 2. 使用

1. 修改配置文件`config.txt`

    1. 在`game_directory=`后输入游戏路径。以`\ProjectZomboid`结尾。默认为`D:\SteamLibrary\steamapps\common\ProjectZomboid`

    2. 在`save_directory=`后输入存档的路径。以`\存档名`结尾。如果你使用的是游戏的默认存档路径，应输入

        ``` 
        C:\Users\用户名\Zomboid\Saves\Sandbox\存档名
        ```

        注意将上面的`用户名`替换为你的Windows系统用户名，将`存档名`替换为存档文件夹的名称，例如`05-11-2022_05-13-27`

2. 运行``run.bat`。请等候若干分钟，运行结束后会在`output`文件夹生成如下命名的两个图片：

    1. `存档名.png`为地图模组所在区域的指示图。
    2. `legends_存档名.png`指示每个颜色所代表的模组。

3. 默认使用字体`msyhbd.ttc`。如需使用其他字体，请替换文件夹`font`中的字体文件。



## 3. 其他

如果我想选择一些模组进行绘制又不想新建存档呢？

事实上本脚本在存档文件夹中只读取了文件`存档名\mods.txt`，所以你可以：

1. 新建一个文件夹。在`config.txt`的`save_directory=`后输入此文件夹的路径。
2. 在此文件夹下新建文件`mods.txt`，每一行是`mod = Mod ID,`，将`MOD ID`替换为模组的ID。模组的ID可在大部分模组的创意工坊页面的底部，或者在模组文件夹中的`mod.info`文件查看。注意保留`=`两边的空格。
3. 运行`run.bat`。
# 中文论文写作检查软件

## 主要功能
- 简单错误检查，目前为叠词/重复词检查。
- 口语化表达检查，根据一些常见的口语化表达关键词。
- AI (zhizhang) 写作查错，例如由于输入法错误造成的错误。

## 所需环境
- Python (低于3.9)
- [pycorrector库](https://github.com/shibing624/pycorrector) （可选）

## 运行方法

在 ```thesis_check.json``` 中，修改必要参数，然后 ```python thesis_check.py``` 运行，得到报告文件

### 参数说明

- ``path`` 为包含目标 ```.tex``` 文件的文件夹
- ``report`` 为检查报告文件
- 口语化用词的列表可以自行进行编辑。

**options** 里面参数说明
| 名称               | 功能        | 参数         |
| ---------------- | --------- | ---------- |
| duplicate_detect | 是否进行叠词检查  | true/false |
| oral_detect      | 是否进行口语化检查 | true/false |
| level            | 口语化检查等级   | 1/2/3      |
| AIcorrect        | 是否AI检查    | true/false |
| corrector_engine | AI 引擎     | kelnm/erine/macbert      |

### 注意点
- 生成的报告文档仅对可能有问题的地方做标注，不提供自动修改。
- 目前仅支持 tex 文档
- 所有检测的对象均是一行文字，因此如果是 MS word 的编辑习惯，一大段文字按照一行处理，对于报告中定位文字内容可能较为困难，建议尽量多断行，控制单行长度。
- AI 引擎个人使用体验：kelnm 速度快，误伤概率高；erine速度慢，准确度高；macbert速度适中，准确度高，但是会把英文/符号这类一起检测，莫名其妙搞出很多无用信息，根据实际需求选用。

## 未完成工作
- [ ] ignore 功能，忽略特定文件/关键词/错误类型
- [ ] MS word 文档支持
- [ ] 训练自定义科研写作语言库

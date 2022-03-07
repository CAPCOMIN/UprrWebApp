# 后端开发文档

[TOC]

>
>
>**Author：zxy**
>
>March 7th, 2022
>
>

## 1 开发环境及工具

- 1.1 操作系统：Windows 10 专业版 21H2（19044.1526）
- 1.2 IDE：PyCharm 2021.3.2 (Professional Edition)，运行时版本: 11.0.13+7-b1751.25 amd64
- 1.3 语言及版本：Python 3.8
- 1.4 后端框架：Flask 2.0.2

> 所需 Python 依赖包详见 requirements.txt 文件。

## 2 主要模块

- 推荐系统（主页）

- 搜索系统

- 用户画像

## 3 推荐系统

推荐系统主要由主页和结果页组成，在后端分别对应两个函数 `home()` 和 `result()`
。为了将Web页面的URL设计的优雅而便于记忆，我们使用Flask框架提供的路由功能，即在函数上方使用 [`route()`](http://docs.jinkan.org/docs/flask/api.html#flask.Flask.route)
装饰器把一个函数绑定到对应的 URL 上，如下所示：

```python
# HomePage
@app.route("/")
def home():
    ...

# ResultPage
@app.route("/result", methods=["GET", "POST"])
def result():
    ...
```

为了提高页面的美观度和交互性，Flask 配备了 [Jinja2](http://jinja.pocoo.org/)
模板引擎，使用 [`render_template()`](http://docs.jinkan.org/docs/flask/api.html#flask.render_template)
方法来渲染模板。例如，在主页中，只需传递两个变量，`version` 和 `max` ，分别表示当前系统版本和最大用户数，因此在 `home()` 函数中可以这样构造：

```python
return render_template("index.html", version=VERSION, max=users.shape[0])
```

这样前端页面就能获取到正确的信息。而在 `result()`
函数中需要将用户输入的数据进行处理并返回处理后的课程推荐信息和其他附加数据，因此函数的构成就更加复杂。用户输入的数据包括被推荐课程的用户ID和推荐课程数目，因此需要收集用户提交的表单信息，并稍作处理传递给`RecommendationGenerator`
类的协同过滤算法相关函数，得到结果后将结果赋给`recomm`变量。与此同时，`tmp/tmp_cossim_mat.txt` 和 `tmp/tmp_recomm_indices.txt`
两个文件记录了运算过程的相关数据，并在模板中返回给前端页面予以显示。

```python
return render_template("result.html", userID=userID - 1, rec_list=recomm, cm_list=lcm, ri_list=lri)
```

前端页面得到数据后需要使用 Jinja2 模板的语法展示这个`list`，以推荐列表为例：

```html
<ol id="div2">
    {% for rec in rec_list %}
        <li>{{ rec }}</li>
    {% endfor %}
</ol>
```

其他数据展示同理。这样，我们就实现了推荐系统的主要功能。

## 4 搜索系统

搜索系统的开发较为顺利，其搜索页和搜索结果页同样在后端分别对应两个函数 `search()` 和 `searchresult()`
，使用Flask框架提供的路由功能，即在函数上方使用 [`route()`](http://docs.jinkan.org/docs/flask/api.html#flask.Flask.route) 装饰器把一个函数绑定到对应的 URL
上，如下所示：

```python
# SearchPage
@app.route("/search")
def search():
    ...

# SearchResultPage
@app.route("/searchresult", methods=["GET", "POST"])
def searchresult():
    ...
```

在搜索页中只需传递一个变量 max，表示当前数据的最大用户数。

```python
return render_template("search.html", max=users.shape[0])
```

搜索系统的实现主要依赖 [Pandas](https://pandas.pydata.org/)
包，Pandas是一个强大的分析结构化数据的工具集；它的使用基础是 [Numpy](https://numpy.org/)（提供高性能的矩阵运算）；用于数据挖掘和数据分析，同时也提供数据清洗功能。在这里，我们主要使用Pandas
DataFrame。DataFrame是Pandas中的一个表格型的数据结构，包含有一组有序的列，每列可以是不同的值类型(数值、字符串、布尔型等)，DataFrame即有行索引也有列索引，可以被看做是由Series组成的字典。

要搜索数据，我们首先要将CSV数据文件读入DataFrame数据结构，需要用到[`read_csv()`](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_csv.html#pandas.read_csv)函数，并设置 `usecols=['courseID', 'userID']`
，以读取需要的两列。由于搜索页面功能包括两类搜索，一种是搜索选某门课的所有学生，一种是搜索某位学生选择了哪些课程，为此需要将 `request.form ` 表单的第一列使用IF语句区分，即可分别实现各自的功能。

得到所需数据的DataFrame后，使用 `studentSearchResult = data[data['courseID'] == course]`
语句即可完成检索。由于Pandas的开发是建立在Numpy的数组结构之上的，它的许多操作都是通过C语言实现的，基于Numpy和Pandas自己的拓展模块来编写的，而这些模块是Cpython编写的，编译成C语言，这样来看，我们无需担心Pandas的检索速度。

此时`studentSearchResult` 变量仍是DataFrame数据结构，需要转为list才更容易显示在前端页面，我们只选择需要的列然后使用`to_list()`
函数即可，最后返回使用 [`render_template()`](http://docs.jinkan.org/docs/flask/api.html#flask.render_template) 方法来渲染的模板。

```python
return render_template("searchresult.html", ID=course, rec_list=studentSearchResult['userID'].to_list())
```

另一类搜索同理。

## 5 用户画像

用户画像模块主要使用Pandas和WordCloud两个依赖包，在后端对于两个函数 `searchportrait()` 和 `userportrait()`
，使用Flask框架提供的路由功能，即在函数上方使用 [`route()`](http://docs.jinkan.org/docs/flask/api.html#flask.Flask.route) 装饰器把一个函数绑定到对应的 URL
上，如下所示：

```python
# SearchPortraitPage
@app.route("/searchportrait")
def searchportrait():
    ...

# UserPortraitPage
@app.route("/userportrait", methods=["GET", "POST"])
def userportrait():
    ...
```

在用户画像主页中只需传递一个变量 max，表示当前数据的最大用户数。

```python
return render_template("/searchportrait.html", max=users.shape[0])
```

用户画像功能同样要用到Pandas包处理数据，输入用户ID后舍去不需要的列，使用`userportrait = data[data['userID'] == user]`语句检索对应用户的课程特征信息，并使用`to_list()`
函数转为list列表。之后将数据切割并存入 features.txt 文件，在`draw_wordcloud()`类内函数中完成剩余处理工作，并生成用户画像。

`jieba.analyse.tfidf()`函数是`jieba`库中使用TF-IDF算法的一个关键词提取函数，可用来分词和统计词频，作为用户画像所需的必要数据。最后使用`generate_from_frequencies()`
函数构建生成用户画像。`WoldCloud`类主要参数：

- `font_path`：将使用的字体的字体路径（OTF 或 TTF）；
- `width`：设置画布的宽度；
- `height`：设置画布的高度；
- `background_color`：WordCloud图像的背景颜色；
- `max_font_size`：最大单词的最大字体大小。如果没有，则使用图像的高度；
- `max_words`：最大字（词）数；
- `scale`：计算和绘图之间的缩放比例。对于大的词云图像，使用比例而不是更大的画布尺寸会明显更快，但可能会导致对单词的拟合更粗糙；
- `repeat`：是否重复单词和短语，直到达到 max_words 或 min_font_size。
- `max_words`：最大字（词）数；
- `max_words`：最大字（词）数；

由于生成函数报错将直接导致系统崩溃，因此需要在关键函数处应用错误处理。

```python
try:
    wc = generateWordcloud.WC()
    freq = wc.draw_wordcloud()
except ValueError:
    print(ValueError)
    return render_template("userportrait.html", userID=user, rec_list=["⚠", ValueError, "WordCould ValueError"],
                           freq_dict=["⚠", ValueError, "WordCould ValueError"])
```

## 6 总结

- 本项目的后端开发是我第一次使用Flask框架构建WSGI服务器来编写Web业务，并在远程服务器部署，同时这也是我第一次完整的Web后端开发工作。

- Flask框架总体而言是一款简单易用，又容易上手的轻量级Web框架。
- 实际参与Web开发虽然会有意料之外的困难，但也有意想不到的惊喜。

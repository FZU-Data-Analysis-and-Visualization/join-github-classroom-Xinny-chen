# 用爬虫获取网页数据：以安居客二手房爬虫为例

本教程面向课堂教学，目标是带学生完整走通一个真实的数据获取流程：

1. 配置 Python 爬虫环境。
2. 使用 Selenium 打开网页。
3. 使用 BeautifulSoup 解析网页内容。
4. 将爬取结果写入 MySQL 数据库。
5. 导出 CSV 文件。
6. 对数据做一个简单分析：统计福州各市区房源数量。

本教程使用的示例仓库：

<https://github.com/weijiayi-1/anjuke-crawler>

本地项目目录示例：

```text
anjuke-crawler-main
```

课堂演示目标：

```text
爬取福州二手房数据 2000 行，导出为 ershoufang_list.csv，并统计每个市区的房源数量。
```

## 一、项目结构说明

当前项目主要文件如下：

```text
anjuke-crawler-main/
├── README.md
├── requirements.txt
├── config.py
├── db.py
├── crawler.py
├── crawl_city.py
├── export_csv.py
└── main.py
```

各文件作用：

| 文件 | 作用 |
|---|---|
| `requirements.txt` | 项目依赖包列表 |
| `config.py` | 数据库连接信息、城市配置 |
| `db.py` | MySQL 建表、插入数据 |
| `crawler.py` | 爬虫核心逻辑：打开网页、解析网页、提取字段 |
| `crawl_city.py` | 按城市运行爬虫的命令行脚本 |
| `export_csv.py` | 从 MySQL 导出 CSV |
| `main.py` | 原仓库默认入口，会按配置列表爬多个城市 |

本教程推荐使用：

```bash
python crawl_city.py fuzhou --limit 2000
```

而不是直接运行：

```bash
python main.py
```

原因是 `main.py` 会按照 `config.py` 中的城市列表批量爬取，不适合课堂上控制时间和数据量。

## 二、爬虫流程概念图

```mermaid
flowchart LR
    A["确定目标网页"] --> B["Selenium 打开网页"]
    B --> C["获取网页 HTML"]
    C --> D["BeautifulSoup 解析 HTML"]
    D --> E["提取标题、价格、面积、市区等字段"]
    E --> F["写入 MySQL 数据库"]
    F --> G["导出 CSV"]
    G --> H["用 Excel / Python / 数据分析工具分析"]
```

在这个项目中，每一条房源数据大致经历下面的过程：

```text
安居客网页 -> Selenium 浏览器 -> HTML 源码 -> BeautifulSoup 解析 -> Python 字典 -> MySQL 表 -> CSV 文件
```

## 三、课前准备

学生电脑需要安装：

1. Python 环境管理工具：Anaconda、Miniconda 或 Miniforge。
2. Google Chrome 浏览器。
3. MySQL 数据库。
4. Git，或者直接下载 ZIP 版项目。

建议教师提前说明：

- Windows 同学建议使用 Anaconda Prompt 或 Miniforge Prompt。
- macOS 同学使用 Terminal 终端。
- 网络环境可能影响 Selenium 自动下载 ChromeDriver，必要时需要配置代理。
- 本教程只用于课程学习和数据分析示范，不建议高频、大规模抓取公开网站。

## 四、Windows 用户环境配置

班级大部分同学是 Windows，建议按本节操作。

### 4.1 安装 Conda

推荐安装 Anaconda 或 Miniconda。

下载入口：

- Anaconda: <https://www.anaconda.com/download>
- Miniconda: <https://docs.conda.io/en/latest/miniconda.html>

安装完成后，打开：

```text
Anaconda Prompt
```

或者：

```text
Miniconda Prompt
```

检查 conda 是否可用：

```bash
conda --version
```

### 4.2 创建课程环境

建议统一使用 Python 3.11 或 3.12，兼容性更稳。

```bash
conda create -n ajk python=3.11
```

激活环境：

```bash
conda activate ajk
```

如果看到命令行前面出现：

```text
(ajk)
```

说明环境已经激活。

### 4.3 获取项目代码

方式一：使用 Git。

```bash
git clone https://github.com/weijiayi-1/anjuke-crawler.git
cd anjuke-crawler
```

方式二：下载 ZIP。

1. 打开 GitHub 仓库页面。
2. 点击 `Code`。
3. 点击 `Download ZIP`。
4. 解压后进入项目文件夹。

Windows 进入文件夹示例：

```bash
cd Desktop\anjuke-crawler-main
```

### 4.4 安装 Python 依赖

在项目文件夹中运行：

```bash
pip install -r requirements.txt
```

依赖包包括：

| 包 | 作用 |
|---|---|
| `requests` | 网络请求 |
| `beautifulsoup4` | HTML 解析 |
| `lxml` | HTML/XML 解析器 |
| `selenium` | 浏览器自动化 |
| `PyMySQL` | 连接 MySQL |
| `urllib3` | 网络底层工具 |

### 4.5 安装 Google Chrome

下载入口：

<https://www.google.com/chrome/>

安装完成后，打开 Chrome，确认可以正常运行。

### 4.6 ChromeDriver 说明

Selenium 4 通常会自动管理 ChromeDriver。正常情况下，代码里写：

```python
driver = webdriver.Chrome(options=option)
```

Selenium 会自动查找 Chrome 浏览器，并下载匹配版本的 ChromeDriver。

如果运行时报错：

```text
Unable to obtain driver for chrome
```

或者：

```text
error sending request for url
```

说明 Selenium 自动下载 ChromeDriver 失败。常见原因是网络无法访问 Google 的下载地址。

解决方式有两种：

方式一：配置代理。

Windows CMD：

```bash
set HTTP_PROXY=http://127.0.0.1:7891
set HTTPS_PROXY=http://127.0.0.1:7891
```

Windows PowerShell：

```powershell
$env:HTTP_PROXY="http://127.0.0.1:7891"
$env:HTTPS_PROXY="http://127.0.0.1:7891"
```

端口需要根据代理软件实际设置调整。比如 Clash Verge 中常见：

```text
HTTP(S) 代理端口：7891
SOCKS 代理端口：7890
混合代理端口：49871
```

方式二：手动下载 ChromeDriver。

Chrome for Testing 下载入口：

<https://googlechromelabs.github.io/chrome-for-testing/>

注意：

- ChromeDriver 主版本号要和 Chrome 主版本号一致。
- 例如 Chrome 是 `148.x.x.x`，ChromeDriver 也应选择 `148.x.x.x`。

查看 Chrome 版本：

1. 打开 Chrome。
2. 地址栏输入：

```text
chrome://version
```

3. 查看版本号。

### 4.7 安装 MySQL

MySQL 下载入口：

<https://dev.mysql.com/downloads/mysql/>

Windows 推荐下载：

```text
MySQL Installer for Windows
```

安装时建议选择：

```text
MySQL Server
MySQL Workbench
MySQL Shell
```

安装过程中会要求设置 root 密码。请记住这个密码，后面要写入 `config.py`。

安装完成后，可以在开始菜单打开：

```text
MySQL Command Line Client
```

或者在 Anaconda Prompt 中运行：

```bash
mysql -u root -p
```

如果提示：

```text
'mysql' 不是内部或外部命令
```

说明 MySQL 没有加入系统 PATH。可以使用 MySQL Command Line Client，或者把 MySQL 的 `bin` 目录加入环境变量。

常见路径类似：

```text
C:\Program Files\MySQL\MySQL Server 8.4\bin
```

## 五、macOS 用户环境配置

### 5.1 创建 conda 环境

```bash
conda create -n ajk python=3.11
conda activate ajk
```

### 5.2 安装项目依赖

```bash
pip install -r requirements.txt
```

### 5.3 安装 MySQL

MySQL 下载入口：

<https://dev.mysql.com/downloads/mysql/>

macOS Apple Silicon 用户选择 ARM 64-bit DMG 安装包。

启动 MySQL：

```bash
sudo /usr/local/mysql/support-files/mysql.server start
```

检查是否启动成功：

```bash
/usr/local/mysql/bin/mysqladmin -u root -p ping
```

如果显示：

```text
mysqld is alive
```

说明 MySQL 正在运行。

如果终端找不到 `mysql` 命令，可以临时使用完整路径：

```bash
/usr/local/mysql/bin/mysql -u root -p
```

也可以把 MySQL 加入 PATH：

```bash
echo 'export PATH="/usr/local/mysql/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### 5.4 macOS 代理配置

如果使用 Clash Verge，且 HTTP(S) 代理端口为 `7891`：

```bash
export HTTP_PROXY=http://127.0.0.1:7891
export HTTPS_PROXY=http://127.0.0.1:7891
```

虽然 Clash 开启了系统代理，但终端程序不一定自动读取系统代理，所以建议显式设置。

## 六、创建数据库

无论 Windows 还是 macOS，都需要先创建数据库。

进入 MySQL：

Windows：

```bash
mysql -u root -p
```

macOS：

```bash
/usr/local/mysql/bin/mysql -u root -p
```

输入 root 密码后，执行：

```sql
CREATE DATABASE IF NOT EXISTS ershoufang CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

查看数据库是否创建成功：

```sql
SHOW DATABASES;
```

退出：

```sql
EXIT;
```

## 七、配置数据库连接

打开项目中的 `config.py`。

示例配置：

```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '你的MySQL密码',
    'database': 'ershoufang',
    'port': 3306,
    'charset': 'utf8mb4'
}
```

注意：

- `password` 要替换成自己的 MySQL root 密码。
- `database` 要和刚才创建的数据库名一致。
- `charset` 建议使用 `utf8mb4`，避免中文乱码。

如果不想使用 root 用户，也可以创建课程专用用户。

进入 MySQL 后执行：

```sql
CREATE USER 'ajk'@'localhost' IDENTIFIED BY '123456';
GRANT ALL PRIVILEGES ON ershoufang.* TO 'ajk'@'localhost';
FLUSH PRIVILEGES;
```

然后 `config.py` 改为：

```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'ajk',
    'password': '123456',
    'database': 'ershoufang',
    'port': 3306,
    'charset': 'utf8mb4'
}
```

## 八、运行爬虫：爬取福州 2000 条数据

### 8.1 Windows CMD

```bash
conda activate ajk
set HTTP_PROXY=http://127.0.0.1:7891
set HTTPS_PROXY=http://127.0.0.1:7891
python crawl_city.py fuzhou --limit 2000
```

### 8.2 Windows PowerShell

```powershell
conda activate ajk
$env:HTTP_PROXY="http://127.0.0.1:7891"
$env:HTTPS_PROXY="http://127.0.0.1:7891"
python crawl_city.py fuzhou --limit 2000
```

### 8.3 macOS Terminal

```bash
conda activate ajk
export HTTP_PROXY=http://127.0.0.1:7891
export HTTPS_PROXY=http://127.0.0.1:7891
python crawl_city.py fuzhou --limit 2000
```

如果不需要代理，可以省略代理命令。

运行时终端会输出类似：

```text
正在爬取: fuzhou
https://fuzhou.anjuke.com/sale/p1-y1/?from=fangjia
1
https://fuzhou.anjuke.com/sale/p2-y1/?from=fangjia
2
...
已达到限制: 2000
本次新增: 2000
```

说明爬虫正在逐页访问安居客福州二手房页面，并把数据写入 MySQL。

## 九、查看数据库中的数据

进入 MySQL：

```bash
mysql -u root -p ershoufang
```

macOS 如果没有配置 PATH：

```bash
/usr/local/mysql/bin/mysql -u root -p ershoufang
```

如果中文显示为问号，先执行：

```sql
SET NAMES utf8mb4;
```

查看表结构：

```sql
DESC ershoufang_list;
```

查看总行数：

```sql
SELECT COUNT(*) AS total FROM ershoufang_list;
```

查看福州数据数量：

```sql
SELECT COUNT(*) AS fuzhou_rows FROM ershoufang_list WHERE 城市='fuzhou';
```

查看最新 20 条数据：

```sql
SELECT id,城市,市区,标题,户型,面积,所属小区,所属区域,总价,均价,房龄 FROM ershoufang_list ORDER BY id DESC LIMIT 20;
```

如果在命令行里想写成一行：

```sql
SELECT id,城市,市区,标题,户型,面积,所属小区,所属区域,总价,均价,房龄 FROM ershoufang_list ORDER BY id DESC LIMIT 20;
```

## 十、导出 CSV

爬取完成后，在项目目录中运行：

```bash
python export_csv.py
```

成功后会输出：

```text
Exported 2000 rows to ershoufang_list.csv
```

项目目录中会生成：

```text
ershoufang_list.csv
```

这个 CSV 使用 `utf-8-sig` 编码，通常可以被 Excel 正确识别中文。

## 十一、统计每个市区有多少房源

### 11.1 使用 Python 统计

在项目目录运行：

```bash
python -c "import csv, collections; rows=list(csv.DictReader(open('ershoufang_list.csv', encoding='utf-8-sig'))); c=collections.Counter((r.get('市区') or '未识别').strip() or '未识别' for r in rows); print('TOTAL', len(rows)); [print(k, v) for k,v in c.most_common()]"
```

本次示例输出：

```text
TOTAL 2000
晋安 744
仓山 708
台江 376
鼓楼 70
闽侯 37
连江 30
马尾 12
平潭 11
长乐 9
福清 3
```

整理成表格：

| 市区 | 房源数 |
|---|---:|
| 晋安 | 744 |
| 仓山 | 708 |
| 台江 | 376 |
| 鼓楼 | 70 |
| 闽侯 | 37 |
| 连江 | 30 |
| 马尾 | 12 |
| 平潭 | 11 |
| 长乐 | 9 |
| 福清 | 3 |

### 11.2 使用 Excel 统计

1. 用 Excel 打开 `ershoufang_list.csv`。
2. 选中数据区域。
3. 点击 `插入`。
4. 点击 `数据透视表`。
5. 把 `市区` 拖到 `行`。
6. 再把 `市区` 拖到 `值`。
7. 值字段汇总方式选择 `计数`。

这样即可得到每个市区的房源数量。

### 11.3 使用 MySQL 统计

进入 MySQL 后执行：

```sql
SELECT 市区, COUNT(*) AS 房源数
FROM ershoufang_list
GROUP BY 市区
ORDER BY 房源数 DESC;
```

一行写法：

```sql
SELECT 市区, COUNT(*) AS 房源数 FROM ershoufang_list GROUP BY 市区 ORDER BY 房源数 DESC;
```

## 十二、核心代码讲解

### 12.1 `requirements.txt`

项目依赖：

```text
requests>=2.28.0
beautifulsoup4>=4.11.0
lxml>=4.9.0
selenium>=4.8.0
PyMySQL>=1.0.0
urllib3>=1.26.0
```

课堂讲解重点：

- Selenium 负责“像人一样打开浏览器”。
- BeautifulSoup 负责“从网页 HTML 中找数据”。
- PyMySQL 负责“把数据写入 MySQL”。

### 12.2 `config.py`

```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '你的MySQL密码',
    'database': 'ershoufang',
    'port': 3306,
    'charset': 'utf8mb4'
}
```

这里保存数据库连接信息。

为什么需要数据库？

因为爬虫会持续产生很多条数据，如果只打印在终端里，程序结束后不方便保存、查询和导出。MySQL 相当于一个结构化的数据仓库。

### 12.3 `db.py`

核心字段：

```python
FIELDS = [
    '城市', '市区', '标题', '户型', '面积', '方位', '楼层', '时间',
    '所属小区', '所属区域', '总价', '均价', '房龄'
]
```

这些字段就是最终 CSV 的列。

建表 SQL：

```python
CREATE_TABLE_SQL = f"""
CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
    id INT AUTO_INCREMENT PRIMARY KEY,
    城市 VARCHAR(64),
    市区 VARCHAR(64),
    标题 VARCHAR(255),
    户型 VARCHAR(64),
    面积 VARCHAR(64),
    方位 VARCHAR(64),
    楼层 VARCHAR(64),
    时间 VARCHAR(64),
    所属小区 VARCHAR(255),
    所属区域 VARCHAR(255),
    总价 VARCHAR(64),
    均价 VARCHAR(64),
    房龄 VARCHAR(32)
) CHARACTER SET utf8mb4;
"""
```

课堂讲解重点：

- `id INT AUTO_INCREMENT PRIMARY KEY`：每条房源自动编号。
- `VARCHAR`：文本字段。
- `utf8mb4`：支持中文。
- `CREATE TABLE IF NOT EXISTS`：如果表不存在就创建，存在就跳过。

插入数据：

```python
def insert_data(self, data: dict):
    keys = ','.join(FIELDS)
    values = ','.join(['%s'] * len(FIELDS))
    sql = f"INSERT INTO {TABLE_NAME} ({keys}) VALUES ({values})"
    vals = [data.get(f, '') for f in FIELDS]
    self.cursor.execute(sql, vals)
    self.conn.commit()
```

这段代码把一个 Python 字典写入 MySQL。

例如：

```python
data = {
    '城市': 'fuzhou',
    '市区': '鼓楼',
    '标题': '某小区二手房',
    '总价': '300万'
}
```

最终会插入数据库的一行。

### 12.4 `crawler.py`

#### 12.4.1 打开浏览器

```python
option = webdriver.ChromeOptions()
option.add_experimental_option('excludeSwitches', ['enable-automation'])
option.add_experimental_option('detach', True)
option.add_argument('--no-sandbox')
driver = webdriver.Chrome(options=option)
```

含义：

- 创建 Chrome 浏览器配置。
- 使用 Selenium 启动 Chrome。
- 后续可以用 `driver.get(url)` 打开网页。

#### 12.4.2 构造 URL

```python
url = f'https://{city_pinyin}.anjuke.com/sale/p{p}-y{y}/?from=fangjia'
```

以福州为例：

```text
https://fuzhou.anjuke.com/sale/p1-y1/?from=fangjia
https://fuzhou.anjuke.com/sale/p2-y1/?from=fangjia
https://fuzhou.anjuke.com/sale/p3-y1/?from=fangjia
```

其中：

- `fuzhou` 表示城市。
- `p1`、`p2`、`p3` 表示页码。
- `y1`、`y2`、`y3`、`y4` 表示房龄筛选条件。

#### 12.4.3 获取网页 HTML

```python
driver.get(url)
time.sleep(3)
soup = BeautifulSoup(driver.page_source, 'lxml')
```

含义：

- `driver.get(url)`：打开网页。
- `time.sleep(3)`：等待网页加载。
- `driver.page_source`：获取网页 HTML。
- `BeautifulSoup(..., 'lxml')`：解析 HTML。

#### 12.4.4 找到房源列表

```python
soup_list = soup.select('.property')
```

`.property` 是 CSS 选择器，用来选中网页中的房源卡片。

课堂可以演示：

1. 打开安居客网页。
2. 右键检查。
3. 找到房源卡片的 HTML。
4. 观察 class 名称。
5. 对应到代码里的 `.property`。

#### 12.4.5 提取字段

例如提取标题：

```python
data['标题'] = sl.select('.property-content-title-name')[0].text
```

提取小区：

```python
data['所属小区'] = sl.select('.property-content-info-comm-name')[0].get_text(strip=True)
```

提取所属区域：

```python
data['所属区域'] = sl.select('.property-content-info-comm-address')[0].get_text(' ', strip=True)
```

提取总价：

```python
total_price_elements = sl.select('.property-price-total')
data['总价'] = total_price_elements[0].text if total_price_elements else 'N/A'
```

这里用了一个安全写法：

```python
if total_price_elements else 'N/A'
```

如果网页上没有这个元素，就填入 `N/A`，避免程序报错。

#### 12.4.6 提取市区

项目中新增了一个函数：

```python
def extract_district(address_text):
    text = re.sub(r'\s+', ' ', address_text).strip()
    if not text:
        return ''

    parts = [part.strip() for part in re.split(r'[-－–—·/|\s]+', text) if part.strip()]
    district = parts[0] if parts else text.split()[0]

    return district
```

它的作用是从 `所属区域` 里提取第一个区县名。

示例：

| 所属区域原文 | 提取市区 |
|---|---|
| `鼓楼 - 东街口` | `鼓楼` |
| `台江-茶亭` | `台江` |
| `闽侯县 上街` | `闽侯县` |
| `仓山/金山` | `仓山` |

然后写入：

```python
data['市区'] = extract_district(data['所属区域'])
```

#### 12.4.7 限制爬取数量

课堂演示不需要无限爬取，所以脚本支持：

```bash
--limit 2000
```

核心代码：

```python
if limit is not None and inserted_count >= limit:
    print(f'已达到限制: {inserted_count}', flush=True)
    return inserted_count
```

每插入一条数据：

```python
inserted_count += 1
```

达到指定条数后自动停止。

### 12.5 `crawl_city.py`

这个脚本负责把城市和限制条数变成命令行参数。

```python
parser.add_argument("city", help="Anjuke city pinyin, for example: fuzhou")
parser.add_argument("--limit", type=int, help="Stop after inserting this many rows.")
```

所以可以这样运行：

```bash
python crawl_city.py fuzhou --limit 2000
```

也可以爬其他城市，例如厦门：

```bash
python crawl_city.py xiamen --limit 1000
```

注意城市拼音必须和安居客 URL 中的城市子域名一致。

### 12.6 `export_csv.py`

导出脚本核心代码：

```python
cursor.execute(f"SELECT * FROM {TABLE_NAME}")
rows = cursor.fetchall()
columns = [desc[0] for desc in cursor.description]
```

含义：

- 从数据库中取出所有数据。
- 自动读取字段名作为 CSV 表头。

写入 CSV：

```python
with open(OUTPUT_FILE, "w", newline="", encoding="utf-8-sig") as file:
    writer = csv.writer(file)
    writer.writerow(columns)
    writer.writerows(rows)
```

这里使用：

```python
encoding="utf-8-sig"
```

原因是 Excel 打开 CSV 时更容易正确识别中文。

## 十三、清空旧数据

如果想重新爬一批数据，可以先清空数据库表。

请谨慎执行，下面命令会删除已经爬取的数据。

```bash
python -c "from db import DB, TABLE_NAME; db=DB(); db.cursor.execute(f'TRUNCATE TABLE {TABLE_NAME}'); db.conn.commit(); db.close(); print('cleared')"
```

删除旧 CSV：

Windows CMD：

```bash
del ershoufang_list.csv
```

macOS：

```bash
rm ershoufang_list.csv
```

## 十四、常见问题

### 问题 1：MySQL 连接失败

报错示例：

```text
Can't connect to MySQL server
```

排查：

1. MySQL 是否启动。
2. `config.py` 中密码是否正确。
3. 数据库 `ershoufang` 是否已经创建。
4. 端口是否是 `3306`。

Windows 可以检查服务：

```text
任务管理器 -> 服务 -> MySQL
```

macOS 可以运行：

```bash
/usr/local/mysql/bin/mysqladmin -u root -p ping
```

### 问题 2：中文显示成问号

进入 MySQL 后执行：

```sql
SET NAMES utf8mb4;
```

并确认 `config.py` 中有：

```python
'charset': 'utf8mb4'
```

### 问题 3：Selenium 找不到 ChromeDriver

报错示例：

```text
Unable to obtain driver for chrome
```

解决：

1. 确认已安装 Google Chrome。
2. 配置代理。
3. 或手动下载 ChromeDriver。

Windows CMD 代理命令：

```bash
set HTTP_PROXY=http://127.0.0.1:7891
set HTTPS_PROXY=http://127.0.0.1:7891
```

macOS 代理命令：

```bash
export HTTP_PROXY=http://127.0.0.1:7891
export HTTPS_PROXY=http://127.0.0.1:7891
```

### 问题 4：网页打开了，但没有爬到数据

可能原因：

1. 网页结构变化，CSS 选择器失效。
2. 网站出现验证码或反爬提示。
3. 网络加载太慢，`time.sleep(3)` 等待时间不够。
4. 页面内容不是当前代码预期的二手房列表。

可以临时把等待时间改长：

```python
time.sleep(5)
```

### 问题 5：运行到一半想停止

在终端按：

```text
Ctrl + C
```

已经写入数据库的数据不会自动删除。下次导出 CSV 时，仍然可以导出已经爬到的数据。

## 十五、课堂演示建议

### 演示 1：先看网页

打开：

```text
https://fuzhou.anjuke.com/sale/
```

让学生观察：

- 一页有多条房源。
- 每条房源有标题、户型、面积、区域、总价、均价。
- 数据是结构化的，适合爬取。

### 演示 2：讲 URL 规律

展示几个 URL：

```text
https://fuzhou.anjuke.com/sale/p1-y1/?from=fangjia
https://fuzhou.anjuke.com/sale/p2-y1/?from=fangjia
https://fuzhou.anjuke.com/sale/p3-y1/?from=fangjia
```

让学生理解：

- `p1`、`p2`、`p3` 控制页码。
- `fuzhou` 控制城市。
- 找到 URL 规律，就可以批量访问页面。

### 演示 3：讲网页元素选择器

在 Chrome 中：

1. 右键房源标题。
2. 点击检查。
3. 查看 HTML class。
4. 对应到代码：

```python
sl.select('.property-content-title-name')
```

让学生理解 CSS 选择器的作用。

### 演示 4：实时写入数据库

爬虫运行时，另开一个终端进入 MySQL：

```sql
SELECT COUNT(*) FROM ershoufang_list;
```

每隔一会儿执行一次，可以看到数据量增加。

### 演示 5：导出 CSV 并做统计

```bash
python export_csv.py
```

然后展示：

```bash
python -c "import csv, collections; rows=list(csv.DictReader(open('ershoufang_list.csv', encoding='utf-8-sig'))); c=collections.Counter((r.get('市区') or '未识别').strip() or '未识别' for r in rows); print('TOTAL', len(rows)); [print(k, v) for k,v in c.most_common()]"
```

引导学生从“获取数据”进入“分析数据”。

## 十六、课堂伦理与合规提醒

爬虫技术本身是中性的，但使用时需要注意：

1. 遵守网站服务条款。
2. 不要高频请求，避免影响网站正常服务。
3. 不要爬取隐私数据。
4. 不要绕过登录、验证码、权限控制。
5. 课堂演示应限制数据量，例如 100 条、500 条、2000 条。
6. 给请求之间设置等待时间，例如 `time.sleep(3)`。

本项目中的等待：

```python
time.sleep(3)
```

就是为了降低请求频率。

## 十七、课后练习

### 练习 1：修改爬取城市

尝试爬取厦门 500 条：

```bash
python crawl_city.py xiamen --limit 500
```

然后导出：

```bash
python export_csv.py
```

### 练习 2：统计不同市区的平均总价

提示：

- `总价` 字段可能包含中文单位。
- 需要先把价格文本转为数值。

可以思考：

```text
总价 = "300万" -> 300
```

### 练习 3：统计不同户型数量

可以按 `户型` 分组：

```sql
SELECT 户型, COUNT(*) AS 数量
FROM ershoufang_list
GROUP BY 户型
ORDER BY 数量 DESC;
```

### 练习 4：绘制市区房源数量柱状图

可以使用：

- Excel 数据透视表。
- Python matplotlib。
- Tableau。
- Power BI。

### 练习 5：增加新的字段

尝试从网页中继续提取：

- 标签信息。
- 房源链接。
- 经纪人信息。
- 发布时间。

需要修改：

1. `FIELDS`
2. `CREATE_TABLE_SQL`
3. `crawler.py` 中的数据提取逻辑
4. 重新建表或给表增加新字段

## 十八、完整课堂命令速查

### Windows CMD

```bash
conda activate ajk
set HTTP_PROXY=http://127.0.0.1:7891
set HTTPS_PROXY=http://127.0.0.1:7891
python crawl_city.py fuzhou --limit 2000
python export_csv.py
```

### Windows PowerShell

```powershell
conda activate ajk
$env:HTTP_PROXY="http://127.0.0.1:7891"
$env:HTTPS_PROXY="http://127.0.0.1:7891"
python crawl_city.py fuzhou --limit 2000
python export_csv.py
```

### macOS

```bash
conda activate ajk
export HTTP_PROXY=http://127.0.0.1:7891
export HTTPS_PROXY=http://127.0.0.1:7891
python crawl_city.py fuzhou --limit 2000
python export_csv.py
```

### 统计市区房源数

```bash
python -c "import csv, collections; rows=list(csv.DictReader(open('ershoufang_list.csv', encoding='utf-8-sig'))); c=collections.Counter((r.get('市区') or '未识别').strip() or '未识别' for r in rows); print('TOTAL', len(rows)); [print(k, v) for k,v in c.most_common()]"
```

### 清空数据库重新开始

```bash
python -c "from db import DB, TABLE_NAME; db=DB(); db.cursor.execute(f'TRUNCATE TABLE {TABLE_NAME}'); db.conn.commit(); db.close(); print('cleared')"
```

## 十九、参考链接

- 项目仓库：<https://github.com/weijiayi-1/anjuke-crawler>
- MySQL 下载：<https://dev.mysql.com/downloads/mysql/>
- Google Chrome：<https://www.google.com/chrome/>
- Chrome for Testing：<https://googlechromelabs.github.io/chrome-for-testing/>
- Selenium 文档：<https://www.selenium.dev/documentation/>
- Conda 文档：<https://docs.conda.io/>

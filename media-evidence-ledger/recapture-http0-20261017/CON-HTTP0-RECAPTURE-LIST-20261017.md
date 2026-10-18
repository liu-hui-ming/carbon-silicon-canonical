# CON HTTP 0 重采清单（796）

路径：`media-evidence-ledger/recapture-http0-20261017/`（不在 `media_archive/` 下）

- **条数**: 796（`media_archive/AUDIT-LATEST.json` → `con_note`: `HTTP 0`）
- **用途**: 在国内 IP 电脑重采 page_screenshot.png（P0：全屏含任务栏时间 + 正文滚动）
- **JSON**（全字段）: CON-HTTP0-RECAPTURE-LIST-20261017.json
- **CSV**（Excel）: CON-HTTP0-RECAPTURE-LIST-20261017.csv
- **纯 URL**: CON-HTTP0-RECAPTURE-LIST-20261017-urls.txt（一行一条）

## 按域名

| 域名 | 条数 |
|------|------|
| www.hsnewsnet.com | 368 |
| www.shangyexinzhi.com | 104 |
| www.ccidnet.com | 84 |
| www.sqxww.com | 76 |
| www.bozhou.cn | 65 |
| www.jmnews.cn | 45 |
| www.lfnews.cn | 28 |
| www.jinandushi.com.cn | 7 |
| www.chinadevelopment.com.cn | 4 |
| www.zidonghua.com.cn | 3 |
| hxxw.ningxia-sc.cn | 2 |
| lfnews.cn | 2 |
| www.cneo.com.cn | 2 |
| www.jinriwenzhai.com | 2 |
| news.ahwang.cn | 1 |
| www.e0734.com | 1 |
| www.weeky.net.cn | 1 |
| www.zghhzx.net | 1 |

## 重采写回

1. 在 **e:\carbon-silicon-canonical**（或同步的 media-evidence-archive 分支）打开 CSV，按 url 访问。
2. 截图覆盖 **`media_archive/<folder>/page_screenshot.png`**（文件夹名见 CSV 的 `folder` 列，勿新建目录）。
3. 若正文可读，同步更新同目录 **`article_source.txt`** 头里 **`HTTP：`** 与正文；重算该目录 `manifest.fragment.json` / 总 manifest（回传后可跑批处理脚本）。

## 备注

- 另有 **1** 条 `article_source` 为 HTTP 0 但 `con_note` 为「源链接已失效…HTTP 0」，未列入本清单。
- 域名集中在 **hsnewsnet.com（368）**、**shangyexinzhi.com（104）**、**ccidnet.com（84）** 等，建议按域名分批。
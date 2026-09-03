# Note Revision Log (Full-Stack Edition)

> **Document Language**: English. **Working Language**: new entries may be written in Traditional Chinese (繁體中文), since teaching is delivered in Traditional Chinese.
> **Version**: 3.0 (Roadmap-Aware). Paired with `teacher-persona.md`, `system.md`, and `fullstack-learning-roadmap.canvas.tsx`.
> **⛔ Append-only**: records are never deleted, cleared, or rewritten. Status changes edit only the `Status` line; archiving relocates a record with its full text intact.

> This document is used to record note revision needs discovered during "Professor K Full-Stack Edition" teaching conversations, to facilitate future updates to the original notes (e.g., `drf-demo/筆記.md`, DRF Serializer notes, Django REST Framework Study Checklist, etc.).

## Record Format Description

Each record includes:
- **Timestamp**: Time of the record
- **Type**: Addition / Modification / Deletion / Clarification / Supplement / Risk / Initialization
- **Section**: Related chapter or concept — name the note file and the checklist item where possible (e.g. `drf-demo/筆記.md` §23, checklist `drf-csrf-api`)
- **Roadmap Phase** *(new in 3.0)*: which phase in `fullstack-learning-roadmap.canvas.tsx` — `react-finish` / `drf` / `integrate` / `docker` / `fundamentals` / `portfolio` / `system`
- **Original Content**: Relevant content from the original notes
- **Issue Description**: Identified problem or point needing improvement
- **Suggested Revision**: Specific revision suggestion
- **Verification Level** *(new in 3.0)*: **L0** 沒碰過 / **L1** 問答驗過 / **L2** 真碼落地（說得出檔名＋函式名）/ **L3** 端對端實測（貼出真實輸出）
- **Trigger** *(new in 3.0)*: what produced this record — 學習者需 2 次以上追問 / 先行失敗預測落空 / 支持階梯升到 S4–S5 / checklist 與 repo 不一致 / 架構決策 / 未完成的收尾 / 時程調整
- **Priority**: High / Medium / Low
- **Status**: Pending / Processed / Archived
- **Deadline Impact** *(new in 3.0)*: Blocking（卡住 8/31 必交付）/ Non-blocking / Post-8/31

### Verification Level Rules (why this field exists)
Record 6 exposed the core failure mode of this system: a checklist item was ticked because it had been "verified through Socratic questioning," while the real repo had no `owner` field and no `permission_classes`. From now on:
- A checklist item may only be ticked at the level actually reached, and the level must be named.
- **L1 may never be reported as done**, and may never tick a checklist item. Only L2 ("已寫、未實測") and L3 count as progress inside the project.
- Any gap between L1 and L2/L3 must leave a **Pending** record here, with its Deadline Impact stated.

### Auto-Trigger Rules (when Professor K MUST append a record)
1. The learner needs **two or more follow-ups** on the same question → the teaching material has a gap.
2. A **Fail-First Lab** prediction differs from the actual output → mental-model gap worth recording.
3. The **Support Ladder reaches S4/S5** (Professor K had to hand over part of the answer) → note gap.
4. A **checklist item is ticked but the repo has no matching code** → Risk record (see Record 6).
5. An **architecture/design decision** is made (e.g. rejecting a third login system, rejecting an `owner` field) → Clarification record including the reasoning, so it can be reused in interviews and the README.
6. A session ends with an **unfinished thread** (route not mounted, no end-to-end test) → Pending record with Deadline Impact.
7. A **roadmap phase slips or is cut** → record what was dropped and what protected the 8/31 must-do deliverables.

### Roadmap Phase Reference (mirror of `fullstack-learning-roadmap.canvas.tsx`)
| Phase id | Mainline | Window | Must-do output |
| --- | --- | --- | --- |
| `react-finish` | React 收尾 + Vite TodoApp | 7/29–8/2 | React 25/25、狀態管理／lifting 已驗收 |
| `drf` | Django REST Framework 核心 | 8/3–8/12 | `listings` API 可 CRUD、React 可 fetch |
| `integrate` | shop React 前台 + DRF 串接 | 8/13–8/24 | shop MVP 本地可 demo |
| `docker` | Docker 入門 + 一鍵啟動 | 8/25–8/31 | `docker compose up` + README |
| `fundamentals` | 後端基本功 | 穿插在 `drf`／`integrate` | HTTP、SQL 索引與 N+1、驗證授權、測試、安全 |
| `portfolio` | 求職包裝 + 第二專案 | 9/1 起 | README、架構圖、履歷、2 次模擬面試 |
| `system` | 教學框架三件套本身 | 隨時 | 人設／工作流／修改記錄的一致性 |

---

## Revision Records

### Pending Records

#### Record 24: `doctor_name` 真落地 L3，但 nullable FK `SkipField` 陷阱需 S1→S2→S4 三級支持階梯才拱出
- **Timestamp**: 2026-08-25
- **Type**: Supplement / Clarification
- **Section**: `listings/serializers.py`；`drf-demo/筆記.md` §33；checklist `drf-nested-serializer`
- **Roadmap Phase**: `drf`（Non-blocking，`docker` 才是今天真正 Blocking 項）
- **Original Content**: §33 把 `drf-nested-serializer` 判定為已驗 ✅／已落地 ❌／深度 D1，止步點寫著「實際跑一次 POST（doctor 送 id）＋ GET 列表端點，親眼確認 `doctor_name` 真的出現」
- **Issue Description**: 學習者把 `doctor_name = serializers.CharField(source='doctor.name', read_only=True)` 加進 `listings/serializers.py`，實測 GET `/listings/api/listings/`，回應同時出現 `"doctor": 1` 與 `"doctor_name": "lin"`，真落地成功。但延伸的 nullable FK `SkipField` 邊界問答連續三次答錯／答不出來：(1) 第一次把 `read_only` 誤用在 `is_valid()`／寫入方向解釋讀取方向的消失現象；(2) 第二次把「找不到 pk」（POST 寫入情境的錯誤）誤套進這個純 GET 情境；(3) 第三次要求完整覆述整條鏈路時直接答「不清楚」。支持階梯升到 **S4**（給出鏈路骨架，留 `AttributeError`／`SkipField` 兩個關鍵詞空格），學習者才填對兩格並完整覆述成功。另確認 erb9 目前 `listings/models.py` 的 `doctor = models.ForeignKey(Doctor, on_delete=models.DO_NOTHING)` 沒有 `null=True`，此陷阱在本專案中永遠不會真的觸發，純屬預防性機制理解。
- **Suggested Revision**: (1) `drf-demo/筆記.md` 可在 §33 後補一段「真落地驗證」小節，貼上這次的真實 GET 回應 JSON 作為 L3 證據；(2) 教材缺口：`read_only`（管寫入是否被驗證）與「這個欄位在 GET 時會不會消失」（管讀取，`to_representation`／`get_attribute`／`SkipField`）兩件事，學習者容易把讀寫方向搞混，建議下次教關聯欄位時先明確畫出「這題問的是 to_internal_value 那條路，還是 to_representation 那條路」再進入細節；(3) 若 erb9 未來真的有 FK 改成 `null=True`（例如 `doctor` 因為醫生離職而可為空），這個陷阱要重新用真程式碼驗證一次，目前僅 L1。
- **Verification Level**: L3（`doctor_name` 落地與真實 GET 回應）／L1（nullable FK `SkipField` 邊界機制，僅問答＋支持階梯 S4）
- **Trigger**: 學習者需 2 次以上追問（實際 3 次）；支持階梯升到 S4（給出鏈路骨架留關鍵詞空格）
- **Priority**: Low
- **Status**: Pending
- **Deadline Impact**: Non-blocking（`drf-nested-serializer` 已落地 ❌→✅；`docker compose` + README 仍是今天起唯一 Blocking 項）

---

#### Record 1: Initialization Record
- **Timestamp**: 2026-08-07
- **Type**: Initialization
- **Section**: System
- **Issue Description**: First-time creation of the Full-Stack Edition revision record system, preparing to collect note revision needs from full-stack teaching conversations
- **Suggested Revision**: During teaching conversations, record content that needs improvement based on the learner's sticking points and common misunderstandings (e.g., unclear parts in the DRF notes or the study checklist)
- **Priority**: High
- **Status**: Pending

---

#### Record 18: Reservation 真落地成果——真實 owner／perform_create／IsOwnerOrReadOnly，並抓出 contacts app 的 FK 反模式
- **Timestamp**: 2026-08-19
- **Type**: Supplement / Correction
- **Section**: Tutorial 4 Authentication & Permissions; checklist `drf-custom-permission`, `drf-perform-create`; new `erb9/reservations` app
- **Roadmap Phase**: `drf` / `integrate`
- **Original Content**: §18/§19/Record 6 previously taught `IsOwnerOrReadOnly`/`perform_create` using a hypothetical "`Listing` has an `owner` field" scenario, and confirmed `Listing`'s real business rule needs no `owner` (role-level `IsAdminOrReadOnly` used instead). A separate correction (2026-08-18→19) had flagged these two checklist items as wrongly ticked to D4 while still 已落地 ❌, and reverted them to D3.
- **Issue Description**: The learner proposed a real resource that genuinely needs object-level owner permission — a reservation system where many users each book their own time slot, unlike `Listing`'s role-level check. While landing it, two anti-patterns surfaced in `contacts/models.py`: `user_id` stored as `IntegerField` instead of `ForeignKey` (no referential integrity once the `User` is deleted), and `listing` stored as `CharField` holding a clinic name instead of a relation (typos or clinic renames can't be tracked) — same root cause as the owner-FK issue being fixed here. Also, in `perform_create()` an anonymous booking makes `self.request.user` an `AnonymousUser`, not `None` — assigning it directly into a `ForeignKey(User)` blows up; this trap never surfaced in the purely abstract walkthrough and only appeared once real code was landed.
- **Suggested Revision**: (1) Add a new section to `筆記.md` writing up the full landing of `Reservation` (`owner` FK + `SET_NULL`, `perform_create`'s `AnonymousUser` branch, `IsOwnerOrReadOnly` with an `is_staff` back door, `read_only_fields`) as a real case study, replacing/supplementing the hypothetical version in §18–19; (2) add a reminder on FK naming convention: the field itself should be named `owner`, not `owner_id` — Django auto-generates the DB-level `owner_id` column, and misnaming it breaks `.owner` access; (3) track separately whether `contacts/models.py`'s `user_id` (`IntegerField`) and `listing` (`CharField`) should be refactored into real FKs (out of scope for this checklist pass, but same problem family); (4) checklist updated: `drf-custom-permission`, `drf-perform-create` 已落地 ❌→✅, depth D3→D4
- **Verification Level**: L2→L3 (real code landed in `erb9/reservations`; full end-to-end permission-chain test follows in Record 19)
- **Trigger**: 架構決策（真正需要物件級 owner 權限的資源）；未完成的收尾（`contacts` app FK 反模式待重構）
- **Priority**: High
- **Status**: Pending
- **Deadline Impact**: Non-blocking (owner/perform_create/IsOwnerOrReadOnly core mechanism is landed; the `contacts` app refactor and note write-up don't block 8/31)

---

#### Record 21: react-props 落地候選架構否決，轉向 Home.jsx `.map()`，尚未確認現狀
- **Timestamp**: 2026-08-21
- **Type**: Clarification / Architecture Decision
- **Section**: `筆記.md` §12；checklist `react-props`；`frontend/src/pages/Home.jsx`
- **Roadmap Phase**: `integrate`
- **Original Content**: 筆記與 checklist 原本假設 props 落地會發生在 `Listing` 詳情頁——把抓回來的 `listing` 傳給一個新開的子元件（如 `ListingDetail`）。
- **Issue Description**: 學生主動質疑「listing 本身就是負責顯示詳情，為了驗證而要寫多餘的元件」，指出這是過度抽象（沒有實際重複利用價值），拒絕為了打勾硬拆元件。回頭比對 Django template `listings.html`／`search.html`，發現同一張卡片 markup 重複出現在兩個頁面，才是真正該抽成元件、用 props 傳資料的 DRY 訊號，因此改判 `react-props` 該落地在 `Home.jsx` 的 `.map()`（抽成 `ListingCard` 元件），而不是 `Listing` 詳情頁。截至下課，學生尚未確認 `Home.jsx` 的 `.map()` 目前是直接寫 JSX 還是已抽成獨立元件，這題懸而未決，課程即結束。
- **Suggested Revision**: (1) 在 `筆記.md` 補記這次架構否決的推理過程（過度抽象 vs DRY 訊號的判斷依據），可直接用在面試「為什麼這樣設計」的回答；(2) 下一堂開場第一題直接問 `Home.jsx` 的 `.map()` 現狀，不重新試探；(3) 若 `.map()` 確認尚未抽成元件，落地任務＝寫出 `ListingCard({ listing })` 並在 `.map()` 內呼叫 `<ListingCard listing={l} />`。
- **Verification Level**: L1（架構判斷經蘇格拉底問答確認，但尚未有任何真程式碼落地，`react-props` 仍記 已落地 ❌）
- **Trigger**: 架構決策（拒絕硬拆子元件，重新定位落地候選位置）；未完成的收尾（`Home.jsx` 現狀未確認，`react-props` 深度仍 D0）
- **Priority**: Medium
- **Status**: Pending
- **Deadline Impact**: Non-blocking（props 落地屬 checklist／程式碼品質項目，不阻擋 shop MVP 本地可 demo 這個 8/31 must-do）

---

### Processed Records

#### Record 32: shop 重整計劃列表 P0–P7 鎖定——客服／店務是第二表面，P7 延後、IA 先寫死
- **Timestamp**: 2026-08-28
- **Type**: Clarification / Architecture Decision
- **Section**: 本 workspace `shop` 重整順序；`products/admin.py`／`orders/admin.py`／`users/admin.py`（過渡期 Django Admin）；Record 31 的領域／邊界決策
- **Roadmap Phase**: `portfolio`（本 repo React + DRF）；P7 客服店務後台 Post-8/31；`fundamentals` 穿插
- **Original Content**: Record 31 已否決先重寫 Product 表、採先 API 邊界後 schema、Cart 先包 session。學習者補充：之後要給**客服與店務**用的自訂 admin（不是推倒商品表），本回合先要一份重整計劃列表；客服／店務後台可以之後再做。
- **Issue Description**: 三個表面必須打同一倉庫：顧客 React 店面、之後的客服／店務 React、過渡期 `django.contrib.admin`。為後台另起一套 Product 表會在第一次對帳互毆。現有 Admin 已能撐過渡——店務：`ProductAdmin` inline 管 variant／圖；客服：`OrderAdmin.search_fields` 含 `order_no`／email／phone。學習者確認清單後本回合**仍不改商店程式碼**（無 DRF、無 `frontend/`）；Cursor todo 勾完只代表清單鎖定，P1–P7 真碼仍是 **L0**。
- **Suggested Revision**:
  **P0 不變（延續 Record 31）**：可賣單位 `ProductVariant`；訂單讀快照不 join 活商品名；`auth.User` + `UserProfile`；Session + CSRF cookie；前綴 `/api/v1/`。
  **P1 目錄唯讀 API（第一段真碼，說「P1 開工」才寫）**：DRF + CORS；`GET /api/v1/categories/`、`GET /api/v1/products/`（分頁 `results`、只 `Product.active`、搜尋 `distinct()`）、`GET /api/v1/products/{slug}/`（variants 含 id／sku／color／size／price／stock + images）；公開 GET；寫入 405 或 `IsAdminOrReadOnly` 佔位；消滅分類迴圈 count 的 N+1。L3：JSON 打得到且 `results` 是陣列。
  **P2 顧客 React**：Vite `frontend/`；列表＋詳情（色／尺寸選到 **variant id**）；`response.ok` 分流；購物車按鈕可不打通。L3：畫面列出真商品。
  **P3 Auth**：`/api/v1/csrf/`、`auth/login/`、`logout/`、`me/`；`credentials: 'include'`。L3：登入後 me 200。
  **P4 Cart API（仍 session，不加表）**：GET／POST／PATCH／DELETE；body 用 `variant_id`；禁止 GET 改數量。L3：加減件後 GET 數量一致。
  **P5 Checkout**：`place_order()` 留 service；`POST /api/v1/orders/` 201／空車 400／缺貨 409；`get_queryset` 只自己的單。L3：成功／409／看別人的單被擋。
  **P6 schema 還債（P1–P5 有測試護欄之後）**：`Cart`+`CartItem` + 登入 merge 寫死一種；`Payment` 當付款真相 + `fulfillment_status`；停 `base_price` 覆蓋 variant；封面單一來源；`accounts`／`users` 合併。Size 不拆 app。收藏 through 非阻塞。
  **P7 客服／店務 React（之後做；IA 如下）**：`/staff/*` 或第二 SPA；`is_staff` + 兩組。P6 出貨欄出現前，禁止客服把現有 `Order.status` 當出貨寫入。過渡期繼續 Django Admin。
  - 客服：搜單（order_no／email／phone）；詳情快照唯讀；改出貨／內部備註（備註欄 P6／P7 才加）；會員卡（電話、積分、近單）；不能改 SKU 價、已付金額、刪 `OrderItem`、改 `Payment.transaction_id`。
  - 店務：上／下架、主檔+variant 庫存／價／SKU、分類樹、顏色、多圖、低庫存列表；不能改已成立訂單快照。
  - Staff API（P7 才開寫）：`/api/v1/staff/products/`、`variants/` 庫存；`GET /api/v1/staff/orders/`（全站）；`PATCH staff/orders/{order_no}/` 只出貨欄／備註；客服打店務寫入 → 403。L3：客服改得出貨改不了價；店務改得了庫存改不了快照。
  **明確不做**：真金流、優惠券／稅／運費、多倉、ES、為後台另起商品表、刪光 templates、P7 提前到 P1 之前。
  開工令：下一刀必須出現「P1 開工」才寫 `serializers.py`／`frontend/`。
- **Verification Level**: L1（清單與 IA 寫進 log）；P1–P7 程式碼 **L0**（不准把本記錄誤報成 API 已落地）
- **Trigger**: 架構決策（客服／店務＝第二表面；P7 延後；IA 先寫死）；未完成的收尾（P1 真碼尚未開工，屬預期延後）
- **Priority**: High
- **Status**: Processed
- **Deadline Impact**: Post-8/31（P1–P7 本 repo）；Non-blocking 對 erb9 docker compose。P1–P2 若無上限開工仍會壓縮 Record 30 的 Docker 窗口

---

#### Record 31: shop 商業網店架構診斷——否決先重寫表，採先 API 邊界、後 Cart 表與訂單狀態機
- **Timestamp**: 2026-08-28
- **Type**: Clarification / Architecture Decision
- **Section**: 本 workspace `shop`（`products`／`orders`／`carts`／`accounts`／`users`）；對照 erb9 人設——兩套程式不可混帳
- **Roadmap Phase**: `portfolio`（Post-8/31 主線）／本 repo 的 React + DRF 邊界；`fundamentals` 穿插（N+1、訂單快照）
- **Original Content**: 學習者要求以商業網店為目標、React + DRF、不要純 Django template，並先分析專案結構（含數據庫）且本階段不改代碼。人設與 Record 30 談的是 erb9（`listings`／`Navbar`／`ListingCard`），與此 repo 不是同一套程式。
- **Issue Description**: 對帳 `requirements.txt`、`config/settings.py`、`config/urls.py`、六個 app 的 models／views 後確認：(1) 服飾電商核心已在 `Category` 樹、`Product`、`ProductVariant`（色×尺寸＝SKU／庫存／售價）、`Order`／`OrderItem` 快照、`place_order()` 的 `transaction.atomic` + `select_for_update`；(2) 卡住 SPA 的不是缺 Product 表，而是渲染邊界——全部 `render()` template、沒有 DRF／CORS／`frontend/`；(3) 真 schema 缺口是 `carts/models.py` 空殼（車只活在 `session['carts']`）、`Order.status` 把付款與出貨揉成一欄、`Product.save()` 用 `base_price` 覆蓋所有 variant 價、`Product.image` 與 `ProductImage` 雙軌、`accounts`（有 views 無 models）與 `users`（有 models 無 views）分裂。學習者確認診斷計畫後，本回合仍不寫商店程式碼，只把決策落地到本 log。
- **Suggested Revision**:
  (1) **keep-domain（已確認）**：不重寫、不另起一套 `Product`／`Variant`／`Order`。DRF 以現有 models 為單一來源；Admin 留作營運後台。結帳與購物車的可賣單位是 `ProductVariant.id`，不是 `Product.id`。Order serializer 讀快照欄位，不現場 join 活著的 `Product.name`。會員維持 `auth.User` + `UserProfile`，不造第三套登入。
  (2) **api-boundary（已定順序，本階段不寫碼）**：第一段真碼＝目錄唯讀 `GET /api/v1/products/`（list／detail、分頁契約、搜尋 `distinct()`、拿掉分類迴圈 count 的 N+1）+ React 列表／詳情。Auth／Cart／Checkout 排在其後。認證沿用 Session + CSRF cookie，不先上 JWT。
  (3) **cart-decision（已選）**：先把現有 session `Cart` 包成 API（React 加減數量不必整頁 redirect）；**不同步**新增 `Cart`／`CartItem` 表。登入合併、後台棄車分析留到 schema 還債。
  (4) **schema-debt（延後，有 API 測試護欄之後才 migration）**：Cart 表 + 登入 merge；訂單付款狀態以既有 `Payment` 為真相、出貨另欄／另表；停掉 `base_price` 覆蓋 variant；封面圖單一來源；`accounts`／`users` 合併；收藏可改 through table。不做：金流 webhook、優惠券／稅／運費、把 `Size` 拆成獨立 app、刪光 templates。
  (5) 時程：完整目錄＋車＋結帳＋登入的 SPA ≥ 1–2 週；本診斷 **L1**。8/31 Blocking 若仍是 erb9 的 docker compose + README，不要跟這份藍圖搶同一週的 2–3 小時。
- **Verification Level**: L1（models／urls／requirements 對帳完成；無 serializers、無 React、無端對端 JSON）
- **Trigger**: 架構決策（否決先重寫 Product 表；採先邊界後 schema；Cart 先 session API）
- **Priority**: High
- **Status**: Processed
- **Deadline Impact**: Post-8/31（本 repo 的 React + DRF 商業網店）；Non-blocking 對 erb9 的 8/31 docker compose + README。若把目錄 API 提前塞進 8/28–8/31 且無上限，會再壓縮 Docker 窗口（見 Record 30）

---

#### Record 30: 時程調整——先改善 shop，Docker 窗口壓縮到 8/31 前最後 1–2 天
- **Timestamp**: 2026-08-28
- **Type**: Clarification
- **Section**: `fullstack-learning-roadmap` 階段順序；`teacher-persona.md` 現況；`drf-demo/筆記.md` §12 下一刀
- **Roadmap Phase**: `integrate` 插入 `docker` 之前；`docker` 仍 Blocking
- **Original Content**: 8/25 起 Blocking 項是 `docker compose up` + README；shop MVP（列表／詳情／loading／error／登入）已可本地 demo，剩餘 shop 項標 Non-blocking。
- **Issue Description**: 學習者明確改計畫：先改善 shop 再學 Docker。8/28 距離 8/31 含今天約 4 個日曆天、每日 2–3 小時。Docker 入門實作通常要 1–2 天；shop 若無上限會把 Docker 擠出 8/31。保護項不變：本地可 demo 的 shop + `docker compose up` + README；線上部署本來就可砍。repo 對帳：`Listing.jsx` 已宣告 `VITE_API_URL`（人設舊文過期）；Navbar 仍指向 `/listings/index` 且 `App.jsx` 無該路由；`Home.jsx` `.map()` 仍直接寫 JSX；詳情頁幾乎只渲染 `title`。
- **Suggested Revision**: (1) 人設與 §12 下一刀已改為 shop → Docker；(2) shop 範圍鎖死在「demo 看得出是網站」的缺口，不開新功能（搜尋、預約前台、contacts FK 重構排除在這窗口外）；(3) 最晚 8/30 必須切 Docker，否則 8/31 沒有 compose。
- **Verification Level**: L2（計畫與人設／筆記已改寫；shop 程式碼尚未在本決策回合落地）
- **Trigger**: 時程調整
- **Priority**: High
- **Status**: Processed
- **Deadline Impact**: Blocking 項仍是 docker compose + README，但開工日延後；shop 無上限即 Blocking 風險

---

#### Record 29: `as_view({...})` 手動綁定機制 L3——405 vs 404 用 `setattr`／`getattr` 原始碼推完整條鏈
- **Timestamp**: 2026-08-28
- **Type**: Supplement
- **Section**: `drf-demo/tutorial/6-viewsets-and-routers.md`「Binding ViewSets to URLs explicitly」；`drf-demo/筆記.md` §38；`doctors/urls.py`（實驗路徑已清除）
- **Roadmap Phase**: `drf`（選修，Non-blocking）
- **Original Content**: 官方 Tutorial 6 在 Router 之前先手綁 `SnippetViewSet.as_view({"get": "list", "post": "create"})`；Record 28（8/27）結案時這段仍是 L0，列為 Pending。
- **Issue Description**: 複習模式 Fail-First：暫時在 `doctors/urls.py` 加 `manual-list/` 路徑掛 `DoctorViewSet.as_view({"get": "list", "post": "create"})`，預測對它送 `DELETE` 會回 404，實測卻是 **405**（`{"detail": "Method \"DELETE\" not allowed."}`）。第一次解釋落差時，學習者把昨天 `get_object()` 沒 pk 的坑錯套過來（「因為沒有 pk」），經指出「這裡不相關」後改用 `viewsets.py` 的 `setattr(self, method, handler)` 迴圈與 `views.py` `dispatch()` 的 `getattr(self, request.method.lower(), self.http_method_not_allowed)` 兩行原始碼重新推導，正確答出：dict 之外的 method 從未被 `setattr` 上 `self`，`dispatch` 找不到才退到 405，跟 URL／pk 無關。收尾覆述 Router 省了什麼，第一輪只給數量（「省 2 次」）、第二輪漏了 detail 網址的 `GET→retrieve`，經追問後補齊完整兩張 dict。
- **Suggested Revision**: 已寫入 `drf-demo/筆記.md` §38，含手動綁定程式碼、`viewsets.py`／`views.py` 原始碼節錄、404 vs 405 判準表。教材缺口：`get_object()` 缺 pk（AssertionError）與 `as_view` 缺 method（405）是兩種不同層級的失效，容易被學習者混成同一組「沒有 pk」——下次教到其中一個時，應主動先劃清楚跟另一個的邊界，而不是等學習者混淆後才拆。
- **Verification Level**: L3（真實 405 回應 + 兩段原始碼機制親口推導完整）
- **Trigger**: 先行失敗預測落空（404 猜成，實際 405）；學習者需 2 次以上追問（誤套 pk 坑；Router 省了什麼覆述兩輪才完整）
- **Priority**: Low
- **Status**: Processed
- **Deadline Impact**: Non-blocking（選修機制封頂；8/31 Blocking 仍是 docker compose + README，今日起僅剩 3 天）

---

#### Record 28: `@action` 真落地 L3；`detail=False` 被連講成「多筆」，`get_object()` 預測 None 實測 AssertionError
- **Timestamp**: 2026-08-27
- **Type**: Supplement / Clarification
- **Section**: `doctors/views.py`；`drf-demo/筆記.md` §8／§37；checklist `drf-custom-action`
- **Roadmap Phase**: `drf`（選修，Non-blocking）
- **Original Content**: §8 只寫「`@action`：非標準 CRUD 的額外端點（如 `highlight`）」；checklist `drf-custom-action` 整格未驗／未落地。
- **Issue Description**: 初學以「不要覆蓋 `retrieve`」建立加按鈕直覺。Fail-First：`@action(detail=True) available_slots` 一次 200（學習者跳過預測）；改 `detail=False` 打舊 URL 404（Django 列出 `^doctors-viewsets/available_slots/$`）；`detail=False` 仍呼叫 `get_object()` 打新 URL → AssertionError（`pk` not in `self.kwargs`），學習者預測「變成 None」。`detail` 判準連講三次偏成「詳情／列表／做多個／接收多筆」，收到「URL 缺 pk → 不能 `get_object`」才對。學習者主動指出教材只證明 False 會炸、沒證明 False 有用，補 `stats` + `get_queryset().count()`，實測 `{"total": 4}`。
- **Suggested Revision**: (1) 已寫入 §37；(2) 教 `detail` 時先釘「要不要 pk」，禁止用「一筆／多筆」當主角；(3) Fail-First 第一槍若一次過，必須立刻補「有用面」對照，不能只留破壞面；(4) 強調 `get_object()` 讀 `self.kwargs`，方法參數 `pk=None` 是假線索。
- **Verification Level**: L3
- **Trigger**: 學習者需 2 次以上追問（`detail=False` 語意）；先行失敗預測落空（None vs AssertionError）；教材缺口被學習者指出（False 只有破壞面）
- **Priority**: Low
- **Status**: Processed
- **Deadline Impact**: Non-blocking（`drf-custom-action` 已驗 ❌→✅、已落地 ❌→✅；docker 仍是唯一 Blocking）

---

#### Record 27: DRF `PageNumberPagination` 落地並撞出前端契約變更（`data.results`）
- **Timestamp**: 2026-08-27
- **Type**: Supplement
- **Section**: `config/settings.py`；`frontend/src/pages/Home.jsx`；checklist `drf-pagination`
- **Roadmap Phase**: `drf`（Non-blocking）
- **Original Content**: `drf-pagination` 整格未驗；API 列表端點無分頁，一次回傳全部 listing。
- **Issue Description**: 初學模式正確推導「應在收到請求處切資料」；複習模式在 `settings.py` 加入 `DEFAULT_PAGINATION_CLASS` + `PAGE_SIZE: 6`，Postman 實測回應 `{ count, next, previous, results }`（count=10、results 6 筆、next 指向 page=2）。預測前端 `.map` 會因 state 變成 object 而報 `listings.map is not a function`（方向對）；修正為 `setListings(data.results)` 後 React 首頁正常顯示 6 筆。學習者一度以為畫面超過 6 筆，實為與下方靜態 `#services` 區塊混淆，重數後確認 6 筆無誤。
- **Suggested Revision**: `drf-demo/筆記.md` 補一節：DRF 分頁改變 API 契約（裸陣列 → 包裝 object），前端必須改讀 `results`，並可選用 `next`/`previous` URL 做翻頁；與 Django template `Paginator` 對照（同為後端切，但 DRF 回傳格式不同）。
- **Verification Level**: L3
- **Trigger**: Fail-First 預測（前端 map 報錯）+ 真碼落地 + 端對端實測
- **Priority**: Low
- **Status**: Processed
- **Deadline Impact**: Non-blocking（Tutorial 5 非選修三格全部 ✅；DRF 主線 checklist 非選修項已清空）

---

#### Record 26: `HyperlinkedModelSerializer` 真撞上 `ImproperlyConfigured`，view_name 需帶 namespace 才能過
- **Timestamp**: 2026-08-27
- **Type**: Supplement / Risk
- **Section**: `doctors/serializers.py`；checklist `drf-hyperlinked-model-serializer`、`drf-api-root`
- **Roadmap Phase**: `drf`（Non-blocking，`docker` 才是今天真正 Blocking 項）
- **Original Content**: `drf-hyperlinked-model-serializer`、`drf-api-root` 原本整格「未驗／未落地」，筆記裡沒有任何一節提到 DRF 的 `HyperlinkedIdentityField` 預設猜的 view name 跟 URL namespace 的關係。
- **Issue Description**: 先用初學模式建立「pk 是記號、hyperlink 是可直接動作的指標」的直覺（正確一次過）。轉複習模式後：(1) 問 router 的 URL name 從哪來，猜成「從 prefix」，錯——實測 `router.urls` 印出來證明名字來自 `queryset.model` 的名稱，跟 `prefix` 無關；(2) 把 `DoctorSerializer` 改成 `HyperlinkedModelSerializer` 直接真的在 Postman／Browsable API 撞出 `ImproperlyConfigured: Could not resolve URL for hyperlinked relationship using view name "doctor-detail"`——這是官方 Tutorial 5 完全沒教的坑，因為官方範例的 `urls.py` 沒有套 `namespace`，而 erb9 的 `config/urls.py` 用了 `include('doctors.urls', namespace='doctors')`；(3) 學習者自己正確推導出完整 view name 應該是 `doctors:doctor-detail`；(4) 額外追問 `Meta` 裡寫什麼 vs class body 外面寫什麼的規則，以及 `path("", include(router.urls))` 跟 `urlpatterns += router.urls` 的差異（兩者結果相同，只是多包一層 resolver，跟本次錯誤無關，屬於旁支好奇心）；(5) 最終把 `url` 欄位改寫成 `HyperlinkedIdentityField(view_name='doctors:doctor-detail')`，Postman 實測 200，四筆醫生資料都帶出完整 `url`；順手點開 `Api Root`（`GET /doctor/`）也拿到 `{"doctors-viewsets": "http://127.0.0.1:8000/doctor/doctors-viewsets/"}`，`drf-api-root` 一併過關。
- **Suggested Revision**: (1) `drf-demo/筆記.md` 應補一節：`HyperlinkedModelSerializer`／`HyperlinkedIdentityField` 預設猜的 `view_name` 是「不帶 namespace 的裸名字」（`<model小寫>-detail`），如果專案在 `include()` 時加了 `namespace=`，必須手動把 `view_name` 改成 `'<namespace>:<basename>-detail'`，否則會撞 `ImproperlyConfigured`——這是官方 tutorial 完全沒有覆蓋的落差，因為官方範例沒有分 app／沒有 namespace；(2) 補充 `basename`／URL name 的真正來源：`router.register()` 沒給 `basename` 時，DRF 用 `queryset.model._meta.object_name.lower()` 推，跟 `prefix`（純粹決定路徑字串）無關，兩者常被學習者混成一件事；(3) `Meta` vs class body 外面宣告欄位的規則已在對話中講清楚（`Meta` 只管「有沒有、叫什麼」，欄位建構參數必須寫在 class body），可收進筆記當一個小節。
- **Verification Level**: L3（`HyperlinkedModelSerializer` 與 `api_root` 均已在 `doctors` app 落地並經 Postman／Browsable API 實測 200，貼出真實回應截圖）
- **Trigger**: Fail-First Lab 預測與實際不符（第一次以為改型別就會直接成功，實際撞 `ImproperlyConfigured`）；學習者需 2 次以上追問（URL name 來源猜錯、namespace 機制）
- **Priority**: Low
- **Status**: Processed
- **Deadline Impact**: Non-blocking（`drf-hyperlinked-model-serializer`、`drf-api-root` 已落地 ❌→✅ 並達 L3；Tutorial 5 只剩 `drf-pagination` 一格非選修未驗；`docker compose` + README 仍是今天起唯一 Blocking 項，距離 8/31 剩 4 天）

---

#### Record 25: `get_queryset()` 概念清楚但落地卡住，`self` 與 class body 執行時機需 S1→S5 全階梯才拱出
- **Timestamp**: 2026-08-26
- **Type**: Supplement / Risk
- **Section**: `reservations/views.py`；checklist `drf-get-queryset`
- **Roadmap Phase**: `drf`（Non-blocking，`docker` 才是今天真正 Blocking 項）
- **Original Content**: checklist `drf-get-queryset` 原本整格「未驗」，判定為官方 Tutorial 6 收尾項之一，同時是 `reservations` 真程式碼裡一個活著的漏洞：`ReservationList.queryset = Reservation.objects.all()` 沒有依登入者過濾，`IsOwnerOrReadOnly` 只覆寫了 `has_object_permission`（object-level），對 `list()` 端點完全不生效。
- **Issue Description**: 蘇格拉底問答過程如下——(1) 第一次預測「GET 不需要權限」，結果對但機制錯（誤把 SAFE_METHODS 放行等同於「權限系統沒運作」，忽略了 object-level 權限本來就不會作用在 list）；(2) 第二次被問 `has_object_permission` 需要一個具體 `obj`、list 端點哪來的 `obj` 時，答「應該全部每個都傳進去驗證」，誤以為 DRF 會對 list 逐筆跑 `check_object_permissions`；(3) 給出 `ListModelMixin.list()` 與 `RetrieveModelMixin.retrieve()`/`get_object()` 對照原始碼後，正確答出 `list()` 沒有呼叫 `get_object()`；(4) 但被問「要怎麼改 `ReservationList` 讓一般使用者只看自己的」時，只給出「用 if 分流」，且連續兩輪答不出「這個 if 要寫在哪個方法裡」；(5) 給兩段只差「class 屬性」vs「方法」的對照程式碼（S3）後仍答「不清楚」；(6) 給半機制、留 `self` 一個關鍵詞空格（S4）後仍答「不知道」，最終在 S5 由 Professor K 直接給出完整解釋與程式碼；(7) 落地後追問「urls.py 沒寫 get_queryset 為何會被呼叫」，先答錯字方法會被誤呼叫、後修正為「MRO 往上找到 GenericAPIView 預設版」，機制大致正確但誤把預設 `get_queryset()` 的失敗原因講成「找不到資料」，經校正為 `assert self.queryset is not None` 觸發的 `AssertionError`。
- **Suggested Revision**: (1) `drf-demo/筆記.md` 應新增一節專講「class 屬性 vs 方法」的執行時機差異：class body 在 import／class 定義時就執行完畢，此時無 instance、無 `self`、無 `request`；方法要等到有 instance 呼叫時才執行，`self.request` 才存在——這是 `queryset`（屬性）跟 `get_queryset()`（方法）分裂成兩種寫法的第一性原理，且跟 Python OOP 基礎（不是 DRF 專屬）掛鉤，補課時應該先確認學習者對「class body 執行時機」本身的理解，而不是直接跳進 DRF 語彙；(2) 教材缺口：object-level permission（`has_object_permission`）只在 `get_object()` 被呼叫時才生效，這件事目前筆記裡沒有專門段落，只在 D5 `drf-custom-permission` 的推導裡口頭提過，建議獨立成一節，並直接附上 `ListModelMixin`/`RetrieveModelMixin`/`GenericAPIView.get_object()` 三段原始碼作為證據；(3) 補一節「方法覆寫的原理」：`list()` 呼叫 `self.get_queryset()` 完全不依賴 `urls.py` 或任何註冊機制，純粹是 Python 屬性查找沿 MRO 往上找，找到子類別自己的版本就用子類別的；順帶補充內建 `get_queryset()` 預設實作的第一行是 `assert self.queryset is not None`，失敗時是 `AssertionError` 不是查詢失敗。
- **Verification Level**: L3（`get_queryset()` 已寫進 `reservations/views.py` 並端對端實測：非 staff 帳號 `tester` GET 回應 `[]`；staff 帳號 GET 回應該筆 `owner: 1` 的真實預約資料，兩次都貼出實際 Browsable API 截圖）
- **Trigger**: 學習者需 2 次以上追問（實際同一問題追問 4 輪，另加「urls.py 沒寫 get_queryset 為何會被呼叫」的覆寫機制追問一輪）；支持階梯升到 S4→S5（Professor K 直接給出答案與程式碼）
- **Priority**: Medium
- **Status**: Processed
- **Deadline Impact**: Non-blocking（`drf-get-queryset` 已落地 ❌→✅ 並達 L3；`docker compose` + README 仍是今天起唯一 Blocking 項；這個漏洞修補完是加分的真案例，可直接用在 README／面試）

---

#### Record 23: 依筆記 §12–§33 對帳回寫 DRF checklist（8/14 水位 → 8/25）
- **Timestamp**: 2026-08-25
- **Type**: Clarification / Supplement
- **Section**: `drf-demo/筆記.md` §12；canvas `drf-learning-checklist`（狀態鍵 `drf-checklist-v4`）
- **Roadmap Phase**: `integrate` → `docker`
- **Original Content**: 活 canvas 與 workspace 副本停在 2026-08-14：`drf-viewset`／`drf-default-router`／`drf-login-e2e-test`／`drf-react-loading-error`／`drf-env-api-url` 等仍 pending；workspace v3 資料多數 `grounded: false`，與筆記 §24–§33 及 erb9 真程式碼不一致。
- **Issue Description**: 學習者要求依筆記更新學習進度。對帳後確認筆記已走到 8/24（含 Reservation L3、DoctorViewSet、login 三堵牆、loading/error D4、nested-serializer D1），但 checklist 沒跟上。同時結案 Record 21 的「現狀未確認」：`Home.jsx` `.map()` 仍直接寫 JSX，沒有 `ListingCard`；`App.jsx` 沒有 `/listings` 路由，Navbar 卻指向 `/listings/index`。另抓到 `Listing.jsx` 使用 `API` 卻未宣告 `VITE_API_URL`。
- **Suggested Revision**: 已回寫活 canvas 與 workspace 副本為已驗／已落地兩級；數字 已驗 40／51、已落地 37／51。只問答沒落地：`drf-tutorial-map`、`drf-validation`（D2）、`drf-nested-serializer`（D1）。`drf-hyperlinked-model-serializer` 維持未驗。Record 21 的「現狀未確認」已用 repo 結案，該記錄本身仍 Pending（`ListingCard` 還沒寫）。
- **Verification Level**: L2（checklist 與 repo 對帳；本次未新跑端對端）
- **Trigger**: checklist 與 repo／筆記不一致
- **Priority**: High
- **Status**: Processed
- **Deadline Impact**: Non-blocking（進度帳對齊不卡交付；今天起 Blocking 項是 docker compose + README）

---

#### Record 22: `drf-custom-permission` D5 封頂，補上 has_permission vs has_object_permission 的選用判準並列對照
- **Timestamp**: 2026-08-22
- **Type**: Supplement / Clarification
- **Section**: `筆記.md` §31（新增）；相關舊段 §18／§20／§27／§28／§29；checklist `drf-custom-permission`
- **Roadmap Phase**: `drf` / `integrate`
- **Original Content**: §18 記了 permission 與 object owner 的概念、§20 記了 `IsAdminOrReadOnly` 落地、§28 記了 `IsOwnerOrReadOnly` 真落地、§29 記了三段端對端實測——但沒有任何一段把 `listings/permissions.py` 的 `IsAdminOrReadOnly` 與 `reservations/permissions.py` 的 `IsOwnerOrReadOnly` **並列**，說明「為什麼一個覆寫 `has_permission`、一個覆寫 `has_object_permission`」的選用判準與執行時序。
- **Issue Description**: 本堂通過 D5 跨端拓撲之後，學生主動反映「`drf-custom-permission` 能解釋一下嗎還是有點模糊」——拓撲層過了，但最基礎的「兩個方法差在哪、什麼決定我該寫哪個」缺一段可回頭查的對照。D5 推導過程也顯示同一缺口：第 1 輪答「想不到」、第 2 輪答「前端請求，檢查有沒有 token」（本專案是 Session auth 非 Token auth，實指 CSRF token）、第 3 輪答「差別在於有沒有 pk」（把手段當成原因）、第 4 輪才推出「要 listing 的創建的人資料做比對，而登入有這個人的資料就行」。中途另有 class 與 instance 混淆（答「是 model 傳入？」）。
- **Suggested Revision**: 新增 `筆記.md` §31，內容含：(1) 兩份 `permissions.py` 並列真程式碼；(2) 六列對照表（覆寫方法／手上有什麼／執行時機／判的問題／業務規則／是否在 list 端點跑）；(3) 選用判準一句話——業務規則要不要看具體那一筆；(4) 前後端兩層閘門同構表（`Login.jsx` CSRF+登入 ↔ `has_permission`；詳情頁編輯按鈕條件渲染 ↔ `has_object_permission`）；(5) 邊界提醒：`has_object_permission` 不在 list 端點生效，列表遮蔽要靠 `get_queryset()`。**已於 2026-08-22 寫入 §31。**
- **Verification Level**: L3（`reservations/permissions.py` 真程式碼 + 2026-08-20 三段端對端實測 403／403／200 已在案；本堂為概念層封頂，未新增程式碼）
- **Trigger**: 學習者需 2 次以上追問（D5 共 4 輪收斂，且通關後仍主動反映「還是有點模糊」）；支持階梯升到 S4（教師直接給出並列對照與執行時序，僅保留最後一句判準由學生自述）
- **Priority**: Medium
- **Status**: Processed
- **Deadline Impact**: Non-blocking（`drf-custom-permission` 已 D5 封頂，權限鏈 L3 已跑通）

---

#### Record 20: loading/error 真落地——response.ok 分流取代死 state，另彙整 fetch 常見小錯
- **Timestamp**: 2026-08-21
- **Type**: Supplement / Correction
- **Section**: `筆記.md` §12 shop MVP 段落；checklist `drf-react-loading-error`
- **Roadmap Phase**: `integrate`
- **Original Content**: 筆記 §12 原本只記著「下一刀：shop MVP listing 詳情頁——loading／error 狀態都要有」，`Home.jsx` 當時的 `loading` state 宣告了卻沒被 JSX 讀到，是死 state；`error` 狀態連宣告都沒有。
- **Issue Description**: 學生在把 `listingDetail()` 寫進 `Listing.jsx` 的過程中，連續三輪重複同一類「async 函式便利小錯」：(1) `useState` 誤從 `react-router-dom` 匯入、(2) 模板字串寫成 `$(...)` 而非 `${...}`、(3) `setListing({data})` 雙重包裝、(4) `catch(loadError)` 跟 state 變數同名造成遮蔽、(5) 對 setter 呼叫多寫了不必要的 `const x = await setX(...)`。這些屬於「無關痛癢的小錯」，當場直接糾正未占用蘇格拉底輪次，但重複出現三次顯示教材裡缺一段「async + useState 寫法檢查清單」。另外學生一度誤以為 `await` 之後的程式碼會「搶跑」（在請求完成前執行）、以及誤以為所有 4 字頭狀態碼都該進 `catch` ——這兩個是機制層的誤解，已用可執行的 JS 排序實驗與 `response.ok` 語意拆除。
- **Suggested Revision**: (1) 在 `筆記.md` 補一段「fetch + useState 常見手誤檢查清單」，條列上述 5 個小錯，供下次寫類似程式碼前自查；(2) 補一段機制筆記：`await` 之後的程式碼保證在該 `await` resolve 後才執行（不會搶跑），並附上可執行驗證片段；(3) 補一段：`response.ok === false` 是「有回話但業務失敗」，只有 `else`／額外分支能設 `error` state，`catch` 只接網路層失敗；(4) `Listing.jsx` 目前 `catch` 分支忘了呼叫 `setLoad(false)`，補記為已知小洞。
- **Verification Level**: L2（學生口頭確認已貼進 `Listing.jsx` 並跑過畫面；未附 Network／Console 截圖或輸出，暫不判 L3）
- **Trigger**: 學習者需 2 次以上追問（`response.ok`／`catch` 分流反覆確認三輪）；先行失敗預測落空（以為 await 後會搶跑，實驗結果 `1 4 2 3` 推翻）
- **Priority**: Medium
- **Status**: Processed
- **Deadline Impact**: Non-blocking（`drf-react-loading-error` 已落地 ✅，shop MVP 詳情頁核心功能已可運作）

---

#### Record 19: Reservation 除錯四連撞與 IsOwnerOrReadOnly 端對端實測完整跑通
- **Timestamp**: 2026-08-20
- **Type**: Supplement / Correction
- **Section**: Tutorial 4 Authentication & Permissions; end-to-end permission-flow checklist item; `筆記.md` §29; `erb9/reservations` app
- **Roadmap Phase**: `drf` / `integrate`
- **Original Content**: §28's sticking point (1) — "opening `Reservation` as an independent Django app... currently only exists in notes and conversation, not yet actually running inside erb9's project folder structure"
- **Issue Description**: The learner moved §28's code into the real erb9 project (app added to `INSTALLED_APPS`, mounted in the root `urls.py`), and hit four real bugs across four different layers along the way: (1) `serializers.py`'s `ReservationSerializer` failed to inherit `serializers.ModelSerializer` and was missing its import, causing `TypeError: ReservationSerializer() takes no arguments`; (2) `views.py`'s `ReservationDetail` misspelled `queryset` as `queryest`, causing an `AssertionError`; (3) the new app's model never had `makemigrations`/`migrate` run, causing `ProgrammingError: relation "reservations_reservation" does not exist`; (4) `admin.py`'s `ReservationAdmin` put the same field `listing` in both `list_display_links` and `list_editable`, triggering the `admin.E123` SystemCheckError. All four bugs were diagnosed and fixed by the learner reading the traceback/error message unaided. After fixing, three real end-to-end tests were run: anonymous PATCH → 403 (`Authentication credentials were not provided.`); authenticated non-owner PUT → 403 (`You do not have permission to perform this action.`); owner's own PUT → 200 OK, update succeeded.
- **Suggested Revision**: (1) `筆記.md` now has a new §29 writing up the four bugs and the full test results as a real case study; (2) note for future teaching: whenever an anonymous request triggers any permission failure (whether `has_permission` or `has_object_permission`), DRF shows `NotAuthenticated`'s message first as long as there's no `successful_authenticator` — this is easy to misread as "simply not logged in" rather than "object-ownership check failed", worth calling out explicitly when teaching `permission_denied()`'s internal logic; (3) end-to-end permission-flow checklist item updated: 已落地 ❌→✅, depth → D4; (4) Record 18's `contacts/models.py` FK anti-pattern refactor remains pending and is not repeated here
- **Verification Level**: L3 (three real HTTP requests, not hypothetical: anonymous 403, non-owner 403, owner 200 OK)
- **Trigger**: 未完成的收尾（§28 止步點）今日完成收尾
- **Priority**: Medium
- **Status**: Processed
- **Deadline Impact**: Non-blocking

---

#### Record 17: D4 封頂違規自我更正，`drf-generic-views`／`mixins`／`detail-endpoint` 正式推進 D5（React props ↔ Django ownership 跨端拓撲通過）
- **Timestamp**: 2026-08-19
- **Type**: Clarification / Risk
- **Section**: system.md 落地閘門條款；checklist `drf-perform-create`、`drf-custom-permission`、`drf-generic-views`、`drf-mixins`、`drf-detail-endpoint`
- **Roadmap Phase**: `drf` / `system`
- **Original Content**: 2026-08-18 晚間把 `drf-perform-create`、`drf-custom-permission`（兩項當時「已落地」皆為 ❌）用「預約」假設���境的 D4 抽象推演，直接登記成已驗 ✅／深度 D4
- **Issue Description**: 違反 system.md「已落地 ❌ 的項目封頂 D3，不准用假設情境硬上 D4／D5」這條鐵律（教學品質自評破功類型 11：提前開鷤）。今日開場自行發現此違規
- **Suggested Revision**: 已更正回寫：`drf-perform-create`、`drf-custom-permission` 退回深度 D3（已驗 ✅／已落地 ❌ 維持不變）；D4 的評分權轉記在真正已落地 ✅ 的 `drf-generic-views`／`drf-mixins`／`drf-detail-endpoint`（同一套 `has_object_permission()`／`get_object()` 機制）。隨後同一堂課完成 D5 跨端拓撲：學習者自行推出「React `props` 與 Django 資料庫紀錄，只能由發送者（父層／後端）修改，接收者只能發請求，不能自行修改」——把物件擁有權寫入控制的機制，從 Django 抽象搬到 React 元件樹，判定為同構通過。三項 checklist 正式登記深度 D5
- **Verification Level**: L1（問答層級推演＋跨域類比）——`drf-generic-views`／`mixins`／`detail-endpoint` 本身仍是 L2/L3（已落地），本條只補上深度層級的機制理解
- **Trigger**: checklist 與落地閘門規則不一致（自我稽核發現）；跨域類比同構通過（D5 判準）
- **Priority**: High
- **Status**: Processed
- **Deadline Impact**: Non-blocking——DRF 權限鏈核心理解已到頂，但 `drf-perform-create`／`drf-custom-permission`／`drf-owner-readonly`／`drf-owner-none-problem`／`drf-object-permission-flow`／`drf-permission-classes` 這一叢仍待真的寫進 erb9（建議下一刀優先落地，一次性讓這幾格翻綠並解鎖真正的 D4 起跳）

---

#### Record 16: 物件擁有權完整配方 D4 抽象推演（「預約」假設情境）
- **Timestamp**: 2026-08-18（晚）
- **Type**: Supplement
- **Section**: Tutorial 4 Authentication & Permissions；checklist `drf-perform-create`、`drf-custom-permission`、`drf-owner-readonly`、`drf-owner-none-problem`、`drf-object-permission-flow`
- **Roadmap Phase**: `drf`
- **Original Content**: `drf-owner-not-grounded` 已確認 erb9 不需要 owner 欄位（記錄 6），因此 owner／`perform_create`／`read_only_fields`／`has_object_permission()` 這套配方在真專案裡從未被逼過
- **Issue Description**: 需要在沒有真程式碼可對照的情況下，測試學習者是否已把四塊拼圖（FK owner 欄位、`has_object_permission()` 只在 `get_object()` 路徑生效、`read_only_fields` 排除欄位、`perform_create()` 補寫 `request.user`）內化成一套可搬到任何新資源上的抽象配方
- **Suggested Revision**: 以假設「預約」資源逐輪拆解：型別不 match（字串 vs User 物件）→ ForeignKey 概念 → `has_object_permission()` 只由 `get_object()` 呼叫、create 路徑沒有既存物件因此不會經過它 → `read_only_fields` 排除欄位而非驗證 → `perform_create()` 才是實際寫入 `request.user` 的位置。學習者最終完整覆述整套鏈路。**風險**：此推演僅為假設情境，不構成「已落地」，隔天（見記錄 17）發現直接登記 D4 違反封頂規則並已更正
- **Verification Level**: L1（純問答推演，無對應真程式碼）
- **Trigger**: 支持階梯升到 S4–S5（多輪需直接給出術語名稱：ForeignKey、`perform_create()`）
- **Priority**: Medium
- **Status**: Processed
- **Deadline Impact**: Non-blocking（機制已理解，落地仍待排入 `drf`／`integrate` 階段）

---

#### Record 15: patch/put 呼叫方向反轉與 UpdateModelMixin 拼字誤記
- **Timestamp**: 2026-08-18
- **Type**: Clarification / Supplement
- **Section**: Tutorial 3 Class-based Views；checklist `drf-generic-views`、`drf-mixins`、`drf-detail-endpoint`
- **Roadmap Phase**: `drf`
- **Original Content**: 記錄 13 的止步點原記錄「PATCH 轉呼叫的方法名猜成「update_object()」「`DestroyModelMixin` 猜成「DeleteModelMixin」
- **Issue Description**: 重考時上述兩項本身答對，但過程中冒出兩個新小錯：(1) `UpdateModelMixin` 打成 `UpdateModMixin`；(2) 一度講反呼叫方向，說成「`partial_update()` 呼叫 `put()`」——實際上 `put()`／`patch()` 是被 `dispatch()` 用 `getattr()` 分別直接呼叫的兩個平行轉發方法，`patch()` 才轉呼叫 `partial_update()`
- **Suggested Revision**: (1) 拼字錯屬小錯，當場放行未糾正；(2) 呼叫方向錯已用矛盾點拆解糾正，學生重講後修正為正確鏈路：`.lower()` → `getattr()` → `patch()` → `partial_update()` → `update(partial=True)`。建議未來範例庫���「`put()`／`patch()` 是平行轉發方法而非誰呼叫誰」列為常見誤解範例
- **Verification Level**: L1→L2（`ListingDetail` 本身已是 L2/L3，本條為機制理解層補完）
- **Trigger**: 學習者需 2 次以上追問；先行失敗預測與實際鏈路不符
- **Priority**: Low
- **Status**: Processed
- **Deadline Impact**: Non-blocking

---

#### Record 14: 教學框架升級 4.0——深度階梯 D1–D5、落地閘門、P0–P7 單堂串接
- **Timestamp**: 2026-08-18
- **Type**: Modification
- **Section**: system.md 全文；教師人設（全端版）；學習檢查清單資料庫（新增「深度」「止步點」兩欄）
- **Roadmap Phase**: `system`
- **Original Content**: 3.0 把初學與複習切成互斥雙軌，複習模式的深度動作只在「已驗 ✅」的下一堂才會出現，導致深度永遠被推遲到「明天」
- **Issue Description**: 結構性缺陷——一個知識點打成「已驗 ✅」後，深度從未真正被逼問；12–15 輪／30 分鐘預算下，每堂課都停在命名階段就收工。記錄 6 的假水位、Notion 側記錄 15／16 的落地欄位全空，都是同一個病的不同症狀
- **Suggested Revision**: 升級為 4.0：單堂串接 P0–P5（接生）→ 通關檢定＋切換宣告 → P6 深度鷤打（D1–D5）→ P7 雙段收尾；設落地閘門（`已落地 ❌` 當堂封頂 D3）；通關判準改為「用自己的話完整解釋一次」；時間預算 30 分鐘固定、前段 18／後段 12 分帳；資料庫新增「深度」「止步點」兩欄，深度可跨堂累積
- **Verification Level**: L2（三份文件已實際改寫並在 2026-08-18～19 兩堂課實測跑過 P6／P7）
- **Trigger**: roadmap 稽核發現「已驗 ✅ 但深度從未被記錄」
- **Priority**: High
- **Status**: Processed
- **Deadline Impact**: Non-blocking，但直接影響後���所有教學階段的深度追蹤品質

---

#### Record 13: RetrieveUpdateDestroyAPIView 複習模式驗證完成，「屬性名稱 vs 真正執行方法」思維漏洞模式辨識
- **Timestamp**: 2026-08-18
- **Type**: Clarification / Supplement
- **Section**: Tutorial 3 Class-based Views；`drf-demo/筆記.md` §17（generics 收斂）、新增 §26；checklist `drf-generic-views`
- **Roadmap Phase**: `drf`
- **Original Content**: Record 5 已把 checklist `drf-generic-views` 標為「ListCreate 已驗、Detail 待做」；`listings/views.py` 的 `ListingDetail(generics.RetrieveUpdateDestroyAPIView)` 其實已在 2026-08-17 對帳中確認落地，但「已驗」欄位仍是否
- **Issue Description**: 複習模式逐段拆解 `dispatch()` → mixins → `retrieve`/`update`/`partial_update`/`destroy` → `get_object()`/`lookup_field` 時，學習者反覆把「屬性名稱／類別參照」跟「真正執行的方法」搞混，同一種思維漏洞重複發作四次：(1) 把 `lookup_field` 猜成 `filter_field`；(2) 把找方法的動作猜成 `get()`；(3) 把 PATCH 轉呼叫的方法猜成 `update_object()`（實際是 `partial_update()`）；(4) 把 `DestroyModelMixin` 記成 `DeleteModelMixin`。另外 DELETE 成功狀態碼第一次答錯（猜 200，實際 204 No Content）
- **Suggested Revision**: 已在 `drf-demo/筆記.md` 新增 §26（K教授解剖：RetrieveUpdateDestroyAPIView 的 dispatch／mixins／狀態碼複習），完整記錄 dispatch 骨架程式碼、`partial_update`/`destroy` 內部呼叫鏈、204 邊界、以及思維漏洞記錄；建議下一堂第一題直接考「方法名字＋狀態碼」重述（不用重新試探），並補問 `permission_classes` 對應 `check_permissions()` 這條被岔開沒答完的支線。checklist `drf-generic-views` 對應項目已勾選已驗 ✅（深度標記為 D2，因多處靠支持階梯 S5 直接給答案才過關，非完全獨立推導）
- **Verification Level**: L1（問答＋既有 repo 程式碼交叉驗證）——`ListingDetail` 本身在 2026-08-17 已是 L2/L3（真碼落地＋端對端可用），本輪只補上「已驗」這個機制理解層面的缺口
- **Trigger**: 學習者需 2 次以上追問（多個屬性/方法名稱反覆猜錯）；支持階梯升到 S4–S5（GenericAPIView 名稱、正式方法名、狀態碼皆靠提示給出）
- **Priority**: Medium
- **Status**: Processed
- **Deadline Impact**: Non-blocking（`drf` 階段核心 CRUD 機制已確認理解，不卡 8/31 交付；「屬性 vs 方法」模式建議在後續 `integrate`／`docker` 階段的新程式碼複習中持續追蹤）

---

#### Record 12: 非 staff POST 預測 403，實測卻是 401 credentials not provided
- **Timestamp**: 2026-08-16
- **Type**: Clarification
- **Section**: `listings/permissions.py`；`drf-demo/筆記.md` §20；Record 8 權限鏈實測
- **Roadmap Phase**: `integrate`
- **Original Content**: `IsAdminOrReadOnly` 對非 SAFE 方法回 `request.user.is_staff`；學習者預測已登入非 staff 的 POST 為 403
- **Issue Description**: Fail-First 實測回應為 `{"detail":"Authentication credentials were not provided."}`（NotAuthenticated，401 路徑），不是 PermissionDenied（403）。代表請求抵達時 `successful_authenticator` 為空、`request.user` 仍是匿名——保鑣還沒問到 `is_staff`。可能原因：���先登入、cookie 沒送出、或 `localhost` vs `127.0.0.1` 的跨站 SameSite 讓 session cookie 在 POST 時被扣下
- **Suggested Revision**: 筆記補一層：`has_permission` 回 False 之後，DRF 先看「有沒有認證成功」才決定 401 還是 403；驗證權限鏈必須先在 Request Headers 確認 `sessionid` 有被送出
- **Verification Level**: L1（機制問答中）／實測已見到 401，但原因尚未對上 cookie
- **Trigger**: 先行失敗預測落空
- **Priority**: High
- **Status**: Processed
- **Deadline Impact**: Blocking（卡住 Record 8 的權限鏈 L3）

---

#### Record 8: React 端登入路由掛載與端對端實測尚未完成
- **Timestamp**: 2026-08-12（2026-08-14 更新範圍）
- **Type**: Supplement
- **Section**: Tutorial 4 補充；erb9 + React 串接；`drf-demo/筆記.md` §22、§23；checklist `drf-csrf-api`
- **Issue Description**: CSRF-via-cookie 原理、後端 `csrf_view`／`api_login`、以及 React 端讀 cookie＋帶 `X-CSRFToken` header 的完整 `Login.jsx` 元件（含 `getCookie`、`handleSubmit`、受控表單、成功跳轉／失敗清空密碼）均已完成（見 §23）。尚未完成的只剩：`Login` 元件還沒掛進 `App.jsx` 路由、`Navbar` 沒有導向 `/login` 的連結，也還沒有實際在瀏覽器裡端對端測試登入後的完整權限鏈
- **Suggested Revision**: (1) 在 `App.jsx` 新增 `/login` 路由並 render `Login`；(2) 在 `Navbar` 加上連結；(3) 端對端實測 React 登入後呼叫受 `IsAdminOrReadOnly` 保護的 `listings` API，確認 session cookie／CSRF 權限鏈正確運作
- **Priority**: Medium
- **Status**: Processed

---

#### Record 11: 教學三件套升級為 Roadmap-Aware 3.0（人設／工作流／修改記錄）
- **Timestamp**: 2026-08-15
- **Type**: Modification / Supplement
- **Section**: `teacher-persona.md`、`system.md`、本檔 `note-revision-log.md`；對照第四份文件 `fullstack-learning-roadmap.canvas.tsx`
- **Roadmap Phase**: `system`（跨階段，主要服務 `drf` → `integrate` → `docker`）
- **Original Content**: 三份檔案已從統計力學版改寫成全端版，但仍停留在「通用蘇格拉底流程」：沒有隱喻映射表、沒有依 roadmap 主線分階段的題庫、沒有先行失敗（fail-first）實測環節、筆記模板缺少程式碼／資料流／API 契約區塊、修改記錄沒有驗證層級與自動觸發規則，也沒有任何地方知道 8/31 這條硬底線
- **Issue Description**: 對照每日 2–3hr 的現實預算，舊版容易出現三種失血：(1) 概念問答很爽但 repo 沒落地（Record 6 的老問題）；(2) 一個概念鑽太深燒掉整天額度；(3) 缺 code／API／架構的筆記無法直接拿去寫 README 或應付面試
- **Suggested Revision**: 已完成 3.0 升級。人設新增：學習者現況與截止日、隱喻映射表（含沿用夜店保鑣／白名單／便利梯等既有隱喻）、地獄笑話素材庫、第一性原理拆解表、截止日算術式壓力規則、五級支持階梯、先行失敗與驗證誠實兩條互動鐵律。工作流新增：roadmap-aware 初始化、四大主線＋基本功題庫、State 2.5 先行失敗實驗室（含各階段標準實驗表）、每 5 輪自檢與單一概念時間上限、升級後筆記模板（程式碼證據／資料流／API 契約／驗證層級／checklist 同步）、State 4 自動寫 log、State 5 時程稽核與 `/status` `/fail` `/cut` 等指令、checklist 勾選層級規則、執行環境需求。本檔新增：驗證層級 L0–L3、自動觸發規則、roadmap 階段對照表、Deadline Impact 欄位，並修正統計數字
- **Verification Level**: L2（三份檔案已實際改寫落地）→ 待 L3（下一次真實教學對話完整跑過一輪 State 0 → 5 才算端對端驗證）
- **Trigger**: 使用者要求依「全面清單」把三件套對齊第四份 roadmap；同時 Record 6 的假進度風險需要制度化防呆
- **Priority**: High
- **Status**: Processed
- **Deadline Impact**: Non-blocking（但直接影響 `drf`／`integrate`／`docker` 三階段的教學效率與 8/31 交付品質）

---

#### Record 10: Login.jsx 前端登入表單、getCookie、CSRF fetch 鏈完成
- **Timestamp**: 2026-08-14
- **Type**: Supplement
- **Section**: Tutorial 4 補充；erb9 + React 串接；`drf-demo/筆記.md` §23；checklist `drf-csrf-api`
- **Original Content**: Record 8 指出 React 端讀 cookie＋加 `X-CSRFToken` header 的程式碼尚未寫
- **Issue Description**: 需要從零推導 `getCookie(name)`（`document.cookie` 字串解析）、CSRF＋登入的巢狀 `fetch` 鏈、以及 `Login.jsx` 元件的完整 `useState`／受控輸入／`useNavigate` 邏輯
- **Suggested Revision**: 已完成：`getCookie(name)` 從 `document.cookie` 讀取任意 cookie 值；`handleSubmit` 依序 `fetch('/api/csrf/')` → 讀 `csrftoken` → `fetch('/api/login/')`（帶 `X-CSRFToken`／`Content-Type`／`body`／`credentials: 'include'`）→ 依 `res.ok` 分流：成功 `navigate('/')`、失敗 `setPassword("")`（保留 username）；完整 `Login.jsx` 元件（`useState`、`useNavigate`、受控 `<input>`、`<form onSubmit={handleSubmit}>`）已組裝完成。完整記錄於 `drf-demo/筆記.md` §23
- **Priority**: Medium
- **Status**: Processed

---

#### Record 9: 登入端點收斂決策與後端 api_login／csrf_view 落地
- **Timestamp**: 2026-08-13
- **Type**: Clarification / Supplement
- **Section**: Tutorial 4 補充；erb9 + React 串接；`drf-demo/筆記.md` §22；checklist `drf-login-endpoint-convergence`
- **Original Content**: §21 只確立了 CSRF 傳遞原理，尚未決定新舊登入端點如何並存或收斂
- **Issue Description**: 需要先查證 `accounts` 既有 `login`／`register` 跟 `django.contrib.admin` 是否真的共用同一套系統，才能決定要不要「造第三套登入系統」
- **Suggested Revision**: 已查證 `accounts` 的 `register()`／`login()` 跟 `/admin/login/` 從程式碼層面完全沒有交集，`register()` 建立的也是不帶 `is_staff` 的一般使用者；因此否決「造第三套系統」，改為兩支獨立函式共用同一套 `auth.authenticate`／`auth.login`／session 機制（`login()` 留給舊表單，新增 `api_login()` 給 React）��`api_login()`／`csrf_view()` 已親手除錯完成（Response 資料格式、`user.username`、401 狀態碼、`messages` 框架在 JSON API 下失效、import 缺漏）並掛上 `urls.py`。完整記錄於 `drf-demo/筆記.md` §22
- **Priority**: High
- **Status**: Processed

---

#### Record 7: CORS_ALLOW_CREDENTIALS 概念與落地
- **Timestamp**: 2026-08-12
- **Type**: Supplement
- **Section**: Tutorial 4 補充；`drf-demo/筆記.md` §21
- **Original Content**: §20 只列出「下一步要補 CORS_ALLOW_CREDENTIALS」，尚未實際教過這個設定跟 `CORS_ALLOWED_ORIGINS` 的差異、也未落地
- **Issue Description**: 學習者需要先建立「准許靠近」跟「相信憑證」是兩件事的直覺，並理解瀏覽器規格禁止「萬用字元 origin ＋ 允許憑證」的組合
- **Suggested Revision**: 已用初學模式（夜店保��比喻）建立直覺，並確認學習者理解「兩邊都要主動打開」；已在 `config/settings.py` 加上 `CORS_ALLOW_CREDENTIALS = True`、在 `frontend/src/pages/Home.jsx` 加上 `credentials: 'include'`，兩處都是學習者親自寫的。完整記錄於 `drf-demo/筆記.md` §21
- **Priority**: Medium
- **Status**: Processed

---

#### Record 6: Auth／owner 教學停在假設情境，尚未落地到 erb9 真程式碼
- **Timestamp**: 2026-08-11
- **Type**: Clarification / Risk
- **Section**: Tutorial 4 Authentication & Permissions；`drf-demo/筆記.md` §18、§19、新增 §20；Canvas checklist `t4-auth` 分類
- **Original Content**: §18、§19 用「假設 `Listing` 有 `owner` 欄位」的情境教 `IsOwnerOrReadOnly`／`perform_create`，checklist 也把這幾項打成「completed」，但 erb9 真實程式碼裡 `listings/models.py` 沒有 `owner` 欄位、`listings/views.py` 完全沒有 `permission_classes`
- **Issue Description**: checklist 打勾的標準是「蘇格拉底問答驗過」，但學習者可能誤讀成「這在我的專案裡已經是真的」，造成對專案真實進度的錯覺（迷茫來源）
- **Suggested Revision**: 已與學習者對齊並走完決策：確認 erb9 業務規則是「listing 只能由 admin 新增／管理」，跟哪一筆資料屬於誰無關，因此判定**不需要** `owner` 欄位，物件級（object-level）的 `IsOwnerOrReadOnly` 模式不適用；改為角色級（view-level）判斷。學習者親自推導並寫出 `listings/permissions.py` 的 `IsAdminOrReadOnly`（`has_permission()` + `SAFE_METHODS` + `is_staff`），並掛到 `ListingList`／`ListingDetail` 的 `permission_classes`，已在真程式碼落地，不再只是筆記裡的假設情境。完整推導過程（含 Same-Origin Policy、CSRF、Session vs Token 選型）已寫入 `drf-demo/筆記.md` §20。Canvas checklist `drf-owner-not-grounded` 已勾選完成，`迷茫警報` Callout 已可移除或改為記錄性質
- **Priority**: High
- **Status**: Processed

---

#### Record 5: generics 便利梯拓撲／serializer_class 拼字
- **Timestamp**: 2026-08-10
- **Type**: Supplement / Clarification
- **Section**: Tutorial 3 Class-based Views；`drf-demo/筆記.md` §5、§17
- **Original Content**: §5 有階梯與終點範例，但未畫清「`@api_view`≈`APIView` 同級、generics 才是上層成品」；未記錄屬性名拼字地雷
- **Issue Description**: 學習者把三層當成重複 rival、質疑為何還要 `@api_view`；實作時寫成 `serializers_class` 觸發 AssertionError；中段跳過 mixin 中間層直接上 `ListCreateAPIView`
- **Suggested Revision**: §5 加便利梯拓撲表；新增 §17 解剖；checklist `drf-generic-views` 標 ListCreate 已驗、Detail 待做；mixins 列仍 pending 作選修補課。**已寫入。**
- **Priority**: High
- **Status**: Processed

---

#### Record 4: CBV dispatch / as_view / 繼承括號
- **Timestamp**: 2026-08-09
- **Type**: Supplement
- **Section**: Tutorial 3 Class-based Views；`drf-demo/筆記.md` §5、§16
- **Original Content**: §5 只有 generics 終點範例，未拆 `dispatch`/`as_view`/為何不需 `@api_view`/`class X(Y)` 繼承語法
- **Issue Description**: 學習者把分派歸功於 `@api_view`、混淆 class 繼承括號與函式呼叫括號、不清楚 instance 為何才能掛 request
- **Suggested Revision**: 擴寫 §5 機制表 + 新增 §16 解剖；checklist `drf-apiview` 標「機制已驗、改寫待做」。**已寫入。**
- **Priority**: High
- **Status**: Processed

---

#### Record 3: ForeignKey / PrimaryKeyRelatedField / 驗證牆順序
- **Timestamp**: 2026-08-09
- **Type**: Supplement
- **Section**: Tutorial 1 Serialization（關聯）、Tutorial 5 前哨；`drf-demo/筆記.md` §10、§11、§12、§15
- **Original Content**: 筆記未說明 `ForeignKey` 預設變成 `PrimaryKeyRelatedField`、前端如何取得 pk��`run_validation` 空值先於型別／存在檢查
- **Issue Description**: 學習者誤以為送醫生名字即可、誤把驗證順序記成「型別→空值→存在」；同名時 `SlugRelatedField` 危險未記錄
- **Suggested Revision**: 新增 §15：擴大白名單決策、`get_fields` 指揮鏈、doctors API、POST 201、邊界錯誤表、正確驗證順序。**已於 2026-08-09 寫入並更新 Canvas（含關聯欄位項）。**
- **Priority**: High
- **Status**: Processed

---

#### Record 2: 白名單 vs 資料庫 NOT NULL（欄位遺漏地雷）
- **Timestamp**: 2026-08-08
- **Type**: Supplement
- **Section**: Tutorial 1 Serialization / Tutorial 2 Requests & Responses；`drf-demo/筆記.md` §3、§4、§11、§14
- **Original Content**: 筆記只寫白名單控制 JSON 露出／`is_valid → save` 流程，未說明白名單過關後仍可能被 DB `NOT NULL` 拒收
- **Issue Description**: 實戰 POST 僅送 `title`/`address` 時 `is_valid()` 通過，但 `service`（`IntegerField`）與排隊中的 `doctor`（`ForeignKey`）未進白名單 → `IntegrityError` 500，不是乾淨的 400 + `errors`；初學者易誤以為「白名單顧好就安全」
- **Suggested Revision**: 補充「白名單 vs 資料庫約束」一節：字串類缺值常塞 `''`、數字／外鍵缺值變 `None`；附 erb9 地雷欄位；常見坑表加 `IntegrityError` 列；檢查清單標為已驗收。**已於 2026-08-08 寫入 `drf-demo/筆記.md` 並更新 Canvas checklist。**
- **Priority**: High
- **Status**: Processed

---

### Archived Records
*No archived records yet — nothing in this file is ever deleted. Completed items are relocated here with their full text intact.*

---

## Revision Statistics
- **Total records**: 32
- **Pending**: 4 (Record 1, Record 18, Record 21, Record 24)
- **Processed**: 28 (Records 2–17, 19–20, 22–23, 25–32)
- **Archived**: 0
- **Blocking the 8/31 must-do deliverables**: **docker compose + README**（距離 8/31 含今天約 4 個日曆天，進度仍為 0）。學習者 8/28 決定先改善 shop；Docker 窗口壓縮到最後 1–2 天，最晚 8/30 必須切。Tutorial 6 全數 L3。Record 31–32：本 workspace `shop` 重整列表 P0–P7 已鎖定（清單 L1；P1–P7 真碼 L0），與 erb9 shop polish 不是同一條開工令。下一刀需出現「P1 開工」才寫 API。

> **Statistics fix note (2026-08-15)**: the previous count read Pending 1 / Processed 8. Records 9 and 10 were physically filed under "Pending Records" while marked `Processed`, and Record 1 was not counted at all. Records 9, 10 have been relocated to the Processed section and the totals corrected. **No record text was altered, shortened, or removed.**

---

## Teaching Quality Self-Assessment
*Professor K's self-audit log of teaching-process failures, per system.md's self-eval failure-type taxonomy. This section tracks process defects, distinct from the content/material defects tracked above.*

- **2026-08-17 — Failure Type 7**: 單一概念鑽太深燒掉整堂額度，未在 5 輪自檢點喊停；已加入 system.md 每 5 輪自檢與單一概念時間上限規則作為對策。
- **2026-08-18～19 — Failure Type 11**: 對兩項「已落地 ❌」的 checklist 項目（`drf-perform-create`、`drf-custom-permission`）用「預約」假設情境的 D4 抽象推演，直接登記成已驗 ✅／深度 D4，違反「已落地 ❌ 的項目封頂 D3，不准用假設情境硬上 D4／D5」鐵律。當堂自行發現並更正回寫（見 Record 17），評分權轉記到真正已落地 ✅ 的 `drf-generic-views`／`drf-mixins`／`drf-detail-endpoint`，同堂完成 D5 跨端拓撲判定。
- **2026-08-22 — 輪次預算突破（規則邊界判斷）**: `drf-custom-permission` 的 D5 用掉 4 輪，超過 system.md「一級最多 2 輪」上限。判定理由：學生每一輪都在移動（CSRF → pk → owner 比對），非原地打轉，故未記止步點而續推，最終通關。但第 3 輪仍在重述同一題的抽象問法，應更早改換更小顆粒度的切入（直接問函式簽名多了什麼參數），對策：後段遇到「方向對但語言不足」時，第 2 輪就換成簽名／時序層級的具體問題，而非重複要求學生說出抽象共同點。
- **2026-08-27 — Failure Type（假驗過，L1 被誤標成 L3）**: `drf-api-root` 只因為畫面上碰巧出現「Api Root」麵包屑、Postman 打得通，就被直接標成【已驗／已落地】，學習者從未被問過一句「api_root 是什麼」，事後自己承認「完全不知道」。這正是 Record 6 警告過的失敗模式：把「repo 裡的程式碼恰好會動」跟「學習者理解了機制」混成一件事。當堂已改回 `{ verified: false, grounded: true }`，重新走一輪初學（醫院看板比喻）+ 複習（`SimpleRouter` vs `DefaultRouter` 真跑一次，親眼看到 `api_root` 這條路由連同麵包屑一起消失、只留 `doctor-list`/`doctor-detail`，404 頁面本身就是證據），最終正確蓋章 `{ verified: true, grounded: true }`（L3）。對策：日後任何一格只要沒有經過至少一輪針對該概念本身的提問-回答，就不准標記 verified，即便它是在教別的題目時「順便」出現在畫面上的。
- **2026-08-27 午後 — Fail-First 第一槍跳過預測**：`@action(detail=True)` 學習者沒預測就跑出 200。對策：一次過的實驗仍要先收預測；若漏了，立刻補破壞面（本堂後續 404／AssertionError 有補上）。
- **2026-08-27 午後 — 教材只給破壞面**：`detail=False` 先被教成「會 404／會炸」，學習者主動要求「有用的場合」。對策：對照參數必須成對出現（True 鎖定一筆／False 對整份 queryset 動手），不能只炸給看。

---

## Usage Instructions
1. **When an issue is discovered during a conversation**: append a new record entry to this document — never overwrite an existing one.
2. **Mark processing status**: update only the `Status` line as work progresses; keep the original Issue Description and Suggested Revision as written history.
3. **Periodic archiving**: move completed revisions to the Archived section **with their full text**. Archiving is relocation, never deletion — this file is append-only history.
4. **Every record names a Verification Level and a Deadline Impact**: an entry without them is incomplete, because "understood" and "in the repo before 8/31" are different claims.
5. **Cross-check before ticking any checklist canvas**: L1 never ticks; L2 ticks as「已寫、未實測」; only L3 ticks as done. A ticked item with no code in the repo becomes a Risk record.
6. **At session end, Professor K reports**: records added, statuses changed, and everything still sitting at L1.

## Cross-File Map
| File | Role | What it owns |
| --- | --- | --- |
| `teacher-persona.md` | Character | 語氣、隱喻映射表、地獄笑話庫、第一性原理拆解表、支持階梯 |
| `system.md` | Workflow | State 0–5 狀態機、雙模式題庫、先行失敗實驗室、筆記模板、指令表 |
| `note-revision-log.md` (this file) | Memory | 教材缺陷、架構決策、驗證層級、未完成收尾、統計 |
| `fullstack-learning-roadmap.canvas.tsx` | Authority | 時間軸、階段優先度、8/31 硬底線、後端基本功與求職清單 |
| `drf-demo/筆記.md` + 6 checklist canvases | Content | 實際教材段落（§3–§33）與細部進度勾選 |

---

# ║ shop 專案分帳區（Record 33 起）║

> **建置日：2026-08-28。** 以下為新分帳區。上方 Record 1–32、Revision Statistics、Teaching Quality Self-Assessment、Usage Instructions、Cross-File Map 全部維持原樣，**一字未改**（append-only）。其中與 shop 新規則衝突的部分，以本區的 v2 版本為準，舊文降為歷史記錄。

## 分帳規則（Scope Firewall）

1. **本區只記 shop。** 專案 = 這個 Django repo（`config/` ＋ `products`／`orders`／`carts`／`accounts`／`users`／`pages`，未來加 `frontend/`）。
2. **舊專案（erb9）不得作為依據。** `fullstack-learning-roadmap.canvas.tsx`、`drf-demo/筆記.md`、六份 checklist canvas、`listings`／`reservations`／`doctors` 相關紀錄全部只能引用為「教學失敗模式」，不得引用為 shop 的時程、進度或技術事実。
3. **同名陷阱**：Record 30 以前出現的「shop polish」指的是 erb9 房源案的打磨，**不是本專案**。
4. **權威順序**：repo 真碼 > `shop-rebuild-checklist.md` > 本區記錄 > `system.md` > `teacher-persona.md`。真碼與文件衝突時，改文件，不改現實。
5. **每筆新記錄必須寫兩件事**：`Verification Level`（L0–L3）與 **`Gate Impact`**（影響哪個閘門／幾段預算）。舊格式的 `Deadline Impact` 已廢，因為已經沒有日曆底線。

---

## Record 33 — 教學框架改版 v4.0（Build-First／試錯派）

- **Date**: 2026-08-28
- **Trigger**: 學習者明確下令：不參考舊專案文件、不引用 Notion 頁面；規則與人設以 shop 為主；教學改成「邊寫碼邊講為什麼」；不准先問一堆問題才開工；人設改為「工程知識只能靠不停寫碼＋不停試錯」。
- **Issue Description**: v3.0 的 `system.md` 與 `teacher-persona.md` 建在三個已失效的前提上：（a）**No Direct Answers**（答對才給碼）—— 與「現在要開始習作」直接衝突；（b）**以 8/31 硬底線驅動進度**—— 底線來自舊專案的 roadmap canvas；（c）**Docker 是外部專案的交付物**—— 與 shop 無關卻佔著阻塞項。另外人設檔的隆噂表與範例對話大量指向 `listings`／`Reservation`／`DoctorViewSet`，學習者在 shop 裡永遠找不到對應物。
- **Suggested Revision**: 重寫為 v4.0，已於本日交付三份檔：
  - `system.md` v4.0：**Code First Every Turn**（每輮先出碼）、**No Interrogation Before Work**（問題只能在碼後，最多一問）、**Error Menu Alongside**（每段碼附多種出錯可能）、**Trial-and-Error Is the Curriculum**（L3 需真踩 ≥2）、**Always Give the Correct Version Too**（只炸不給正解是 8/27 已記錄過的教學缺陷）。支持階梯 S1–S5 改成 B1–B3，任何一階都不得「答對才給碼」。
  - `teacher-persona.md` v4.0：Core Identity 改為「工程知識只存在於打過的字與踩過的錯」；新增 Trial-and-Error Coach 人格；隆噂表删除 erb9 那格，改上 shop 專屬隆噂（variant＝真正能結帳的那件、訂單快照＝收據不改寫歷史、`base_price` 覆蓋＝總編輯一支紅筆改接所有分店標價、永遠綠的測試＝從不響的煙霧警報器）；第一性原理表加第三欄「怎麼親手弄壞它來自証」。
  - `shop-rebuild-checklist.md` v2：見 Record 34。
- **Verification Level**: **L2**（三份檔已落地並交付；規則是否真的改得动教學行為，要等 P1.0 跑完一輮才能升 L3）
- **Gate Impact**: 无直接閘門；但 P1.0 之後若教學仍出現「先問三題再給碼」，視為本記錄失效，須開 Record 回寫。
- **Priority**: High
- **Status**: Processed

---

## Record 34 — 期限制度改為軟期限＋Docker 歸 shop＋清單矛盾修正

- **Date**: 2026-08-28
- **Trigger**: 學習者拍板：「兩邊都改，首先更改期限為軟期限跟進度做期限，其次 docker 改用在 shop。」
- **Issue Description**: 三項制度級矛盾：
  1. 舊 Statistics 欄以「距離 8/31 約 4 個日曆天、docker compose + README 進度 0」作為 blocking，但那是外部專案的交付物，跟 shop 的進度沒有因果關係。
  2. 舊清單六個 todo 全標 `completed`，正文卻寫「任一階段沒打到真實 JSON／畫面就還是 L0」—— 這是 Record 6 與 8/27 `drf-api-root` 同一種「假驗過」的結構性重現，只是這次發生在清單的 front-matter。
  3. 舊清單 P0 末條與文末各寫一句「不寫商店程式碼直到你說開工」，而學習者已下開工令。
- **Suggested Revision**:
  - **期限重定義**：取消日曆底線，期限的單位改成**未綠的閘門**。每階段配段數預算（1 段 ≈ 一次 2–3 小時）：P1.0 0.5／P1.1 0.5／P1.2 1／P1.3 0.5／P2 2／P3 1／P4 1.5／P5 1.5／P5.5 1／P8 1.5／P6 2–3／P7 4+。超支處置順序：① 砍非閘門項 ② 降級成 P6／P7 待辦 ③ 降 L2 並登記 ④ 最後才動預算。**軟期限不等於軟閘門。**
  - **Docker 歸 shop**：獨立為 **P8**（`web` ＋ `db` Postgres 的 `docker compose`），預算 1.5 段，可提前到 P2 之後。閘門：clean clone → `cp .env.example .env` → `docker compose up` → P1.2／P3／P4／P5 四個閘門重跑綠。
  - **清單 v2**：只 `p0-lock` 保留 `completed`（決策型，不需真碼），P1 改 `in_progress`，其餘全 `pending`；兩句「不准開工」删除；新增 **P5.5 測試護欄**（舊版把它寫成 P6 前提卻沒有任何階段負責）；P1 拆成 P1.0／P1.1／P1.2／P1.3；解決 P1／P7 的 405 佔位矛盾（**P1 不建 `staff/` 路由**）；mermaid 從壞掉的單行 inline code 改回區塊。
  - **驗收加第二把尺**：「試錯覆蓋率」＝該階段錯誤菜單裡真踩過幾項。`L3 + 0` 標成 **L3（脆）**，不算通關。
- **Verification Level**: **L1**（制度已寫定；任何階段未打到真 JSON／畫面之前一律 L0）
- **Gate Impact**: P1–P5 約 8 段；P8 1.5 段；目前已完成 0 段。現在卡在 P1.0（`curl -i /api/v1/` 不是 404）。
- **Priority**: High
- **Status**: Processed

---

## Record 35 — 九份真碼到位，推翻清單 v2 三項假設

- **Date**: 2026-08-28 13:51
- **Trigger**: 學習者上傳 `pages/urls.py`、`pages/views.py`、`accounts/views.py`、`accounts/urls.py`、`accounts/models.py`、`carts/models.py`、`carts/views.py`、`carts/urls.py`、`carts/cart.py`。
- **Issue Description**: 清單 v2 的三項寫法被真碼推翻，另外發現四個先前不知道的真實地雷：
  1. **被推翻**：P1.0 錯誤菜單 #4 假設「`pages.urls` 可能有 catch-all 吃掉 `api/v1/`」—— 實際 `pages/urls.py` 十條全是具名路徑（`''`、`about/`、`blog/`、`blog/post/`、`subscribe/`、`faqs/`、`shipping_info/`、`return_info/`、`payment_info/`、`test/`），只有 `handler404 = 'pages.views.custom_404'`，**沒有 catch-all**。風險排除。
  2. **被推翻**：P6 第 1 項寫「`carts/models.py` 已存在，需先對帳」—— 實際它是 **57 bytes 的空檔**（只有 `from django.db import models` 與注释）。購物車 **100% 在 session**，Cart／CartItem 是從零建表，不是對帳。
  3. **被修正**：`accounts/models.py` 也是空檔 → `accounts` 只有 views／forms／urls，`UserProfile` 完全在 `users/models.py`。所以 P6 的「accounts vs users 合併」難度遠低於預估（不是兩套 model 打打，是一個 app 只剩殼），可降為非阻塞項。
  4. **新發現（P4 真地雷，比先前推測的嚴重）**：`carts/views.py::carts_add` 接在 `add/<int:variant_id>/`，且 `quantity = int(request.GET.get('quantity', request.POST.get('quantity', 1)))` —— **GET 真的改得動狀態，而且連数量都從 query string 吃**。且全段**沒有任何庫存檢查**，超賣要到 P5 才會發現。
  5. **新發現**：`add_to_cart` 從 POST 拿的是 **`sku` 字串**（不是 `variant_id`），數量欄位名叫 `demo_vertical2`（前端模版残留），且用 `'out-of-stock'` 這個**字串哨兵**判斷缺貨。P4 契約改成 `variant_id` 是對的，但必須認知到與現有模版不兼容。
  6. **新發現**：`carts/cart.py::clear()` 用 `del self.session['carts']`，**同一個 request 裡呼叫兩次就 `KeyError`**。P5 下單成功後要清車，這是真實的 500 來源。另外 `__iter__` 對已從 DB 刪除的 variant 是 `continue` 跳過（**沉默消失**，使用者看不到任何訊息），且取價用**即時** `variant.final_price`，所以 P5 必須自己做快照，購物車本身不提供價格歷史。
  7. **新發現（P1.2 同類錯誤已在 repo 裡真實發生）**：`pages/views.py::index` 用 `Product.objects.all().order_by('?')[:3]` —— 不是 `Product.active`，所以**下架商品會出現在首頁「銀销商品」**（回 200，沉默失敗），且 `order_by('?')` 在 Postgres 上是全表排序。這不是教學範例，是已經上線的 bug。
  8. **正面素材**：`accounts/views.py::order_detail` 已經用 `get_object_or_404(..., order_no=order_no, user=request.user)` —— 這就是 P5 「只看得到自己的單」的現成正確範例，API 只是把它搬到 `get_queryset`。同檔也證実 `Order.items`（related_name）、`Order.payment`（OneToOne）、`UserProfile.points`／`favorites`／`request.user.profile` 都存在。
- **Suggested Revision**: 清單改為 v2.1（本日已實施）：P1.0 菜單 #4 改成已排除並換上真地雷（`api/v1` 尾斜線與 `APPEND_SLASH` 只救 GET）；P4 段改寫為以上六項真實行為；P6 第 1 項改成從零建表；P1.2 菜單加上首頁已存在的 `Product.objects` 洩漏；缺檔清單只剩 `users/models.py`、`orders/models.py`、`orders/services.py`、`orders/views.py`、`.env` 變數名、Python／Postgres 版本。
- **Verification Level**: **L1**（事実已核對真碼，但一行 API 程式碼都還沒寫）
- **Gate Impact**: P1.0 預算不變（0.5 段），風險降低（少一個 catch-all 要查）；P4 預算從 1.5 段上調風險（要同時處理 sku → variant_id 遷移、缺庫存檢查、GET 副作用三件）；P6 第 1 項從「對帳」改成「建表」，工量上調。
- **Priority**: High
- **Status**: Processed

---

## Revision Statistics v2（取代上方 Revision Statistics 的現行數字；舊欄保留作歷史）

- **Total records**: 47（1–32 舊專案區；33–47 shop 區）
- **Pending**: 4（Record 1、18、21、24 —— 全屬舊專案教材，不阻塞 shop）
- **Processed**: 43（Records 2–17、19–20、22–23、25–47）
- **Archived**: 0（本檔仍然從不刪除任何文字）
- **舊「Blocking the 8/31 must-do deliverables」欄位**：**已廢止**。理由：那約定屬外部專案，且已改成軟期限。Docker 以 shop 的 **P8** 形式存續。
- **現行 blocking（以閘門計）**：**P4 未綠**—— Cart API（session 車、`variant_id`、禁止 GET 改狀態）。P1–P3 閘門皆綠（P3 試錯 3/5 通關）。
- **已完成段數**：5.5 ／ 11.5 段（P1–P8，不含 P7）
- **試錯總帳**：P1.0 2/6；P1.1 0/4；P1.2 0/6；P1.3 0/5；P2 1/5；**P3 3/5**

## Cross-File Map v2（shop 專用；取代上方表格作為現行權威）

| File | Role | What it owns |
| --- | --- | --- |
| shop repo（`config/`、六個 app） | **Ground truth** | 任何文件與它衝突時，改文件 |
| `shop-rebuild-checklist.md` v2.7 | Plan | P0–P8 順序、契約、錯誤菜單、閘門、段數預算、試錯總帳 |
| `system.md` v4.0 | Workflow | W0–W6 流程、錯誤菜單格式、B1–B3 支持階梯、L0–L3 ＋ 試錯覆蓋率、指令表 |
| `teacher-persona.md` v4.0 | Character | 語氣、shop 隆噂表、地獅笑話庫、第一性原理＋怎麼弄壞它 |
| `note-revision-log.md`（本檔） | Memory | 教材缺陷、決策、驗証層級、閘門進度、試錯總帳 |
| 舊專案（erb9）的 canvas 與 `drf-demo/筆記.md` | **已隔離** | 只能引用為教學失敗模式，不得引用為 shop 事実或時程 |

## Usage Instructions 補充（v2）

7. `Deadline Impact` 欄位改名為 **`Gate Impact`**：寫影響哪個閘門、影響幾段預算。不得再寫日曆天數。
8. 勾任何 todo 前，除 L3 之外還要檢查**試錯覆蓋率 ≥ 2**；未達標者標 `L3（脆）`，保留 `in_progress`。
9. 每次真踩一個錯，在清單的「踩過的錯」總帳加一行；若該錯暴露文件級缺陷，才升級成本檔的 Record。
10. 任何新 Record 不得引用舊專案檔案作為依據（見分帳規則第 2 條）。

---

## Record 36 — `orders/*` ＋ `.env` 到位：P5 從「寫邏輯」降為「包藄層」，P8 發現真地雷

- **Date**: 2026-08-28 14:05
- **Trigger**: 學習者上傳 `orders/models.py`、`orders/urls.py`、`orders/views.py`、`orders/services.py`、`.env`（本次**未**附 `users/models.py`，仍缺）。
- **Issue Description**:
  1. **P5 範圍被大幅下修**。`orders/services.py::place_order(user, cart, shipping_data, payment_data)` 已經寫得相當完整：`@transaction.atomic`、`select_for_update()` 上鍰、先跑一輮庫存檢查並一次拋出完整缺貨清單（`InsufficientStockError.items`）、`OrderItem` 寫十項快照、`variant.save(update_fields=['stock'])` 扣庫存、`Payment` 建立、`UserProfile.points` 累積、最後回寫 `order.total`／`status`。**所以 P5 不是寫下單邏輯，是寫一層把例外翻譯成 HTTP 狀態碼的薄壳**（1.5 段 → 下修至 1 段，風險集中在錯誤映射而非事務）。
  2. **現行錯誤傳遞方式與 API 契約直接衝突**：`orders/views.py::place_order` 把缺貨原因寫進 `request.session['order_failed_reason']`／`['order_failed_items']` 再 `redirect('orders:failed')`，失敗頁再 `pop()` 出來。API 版必須改成 **409 ＋ `items` JSON**，不得沾 session。
  3. **`OrderItem.order` 的注釋與程式碼相反**：寫 `on_delete=models.PROTECT` 但注釋寫「訂單刪除時，明細一併刪除」（那是 CASCADE 的行為）。實際後果：Admin 刪訂單會吃 `ProtectedError`。屬教材級地雷，保留作 P5.5／P6 教學素材（注釋不是權威，`on_delete` 才是）。
  4. **`Payment.status` 的 `failed` 是死枝**：`services` 一律 `status='success'`，隨後 `order.status='paid'` 無條件寫入。所以「付款真相」目前是假的；P6 把 `Payment` 当真相之前，須先承認這件事。
  5. **`Order` 沒有 `fulfillment_status`**（只有 pending／paid／failed／cancelled）→ 確認 P6 第 2 項必要，且 P7 的客服**絕對不能寫 `Order.status`**（那是付款欄，不是出貨欄）。
  6. **`Order.Meta.indexes` 包含 `Index(fields=['order_no'])`，而 `order_no` 已經 `unique=True`** → 重複索引，寫入成本白付一份。非阻塞，收進 P6。
  7. **`points` 累積用 `int(total)`** → 小數直接截掉（`99.90` → 99），且點數在假付款下也會給。非阻塞。
  8. **待驗證的真風險（不確定，不沒入結論）**：`services` 同時用 `select_related('product','color')` 與 `select_for_update()`。若 `ProductVariant.color` 是 `null=True`，在 PostgreSQL 上會因 LEFT OUTER JOIN 而抱 `FieldError: FOR UPDATE cannot be applied to the nullable side of an outer join`；若為非空則無事。`carts/cart.py` 裡的 `if variant.color:` 曗示可能可空。**待 P5 開工時用一行 shell 自証**（跑一次該 queryset），不得先寫進文件当事実。
  9. **`.env` 格式是 P8 的真地雷**（只記變數名，不記值）：`SECRET_KEY`、`EMAIL_HOST_USER`、`EMAIL_HOST_PASSWORD`、`DB_NAME`、`DB_USER`、`DB_PASSWORD`、`DB_HOST`、`DB_PORT`。寫法是 `KEY = 'value'`（**等號兩側有空白，值帶單引號**）。`python-dotenv` 會幫你 strip 空白與引號，所以本機正常；但 `docker compose` 的 `env_file` 對引號與空白的處理不同，極可能把引號當成值的一部分 → 連到名為 `'nova'`（含引號）的資料庫 → `OperationalError`。另外 `DB_HOST` 目前是本機位址，進容器後必須改成服務名。
  10. **`EMAIL_HOST_USER`／`EMAIL_HOST_PASSWORD` 是死變數**：`config/settings.py` 完全沒有 `EMAIL_*` 設定，寄信程式碼也整段被註解掉（`send_order_confirmation_email`）。「以為寄信設好了」是典型沉默失敗，寫進 P8 `.env.example` 時要標清楚。
  11. **資安事件（需行動，不是教材）**：學習者把真實 `.env` 連值上傳到對話。裡面有真實 Gmail 帳號、一組應用程式密碼、DB 密碼、`SECRET_KEY`。本檔與任何交付物**一律只記變數名，絕不記值**。已從本場起要求他：輪換這三組憑證、確認 `.env` 已在 `.gitignore`、以後只販變數名。
  12. **正面素材**：`orders/views.py::order_success` 又一次用 `get_object_or_404(..., order_no=..., user=request.user)`，與 `accounts` 那次一致 → P5 API 的 `get_queryset` 只要延用同一條規則。`Order` 的 Meta 已有 `ordering = ['-created_at']`，分頁不會因缺少 order_by 而跳行。
- **Suggested Revision**: 清單更新為 v2.2（本日已實施）：P5 重寫成「薄壳 ＋ 錯誤碼翻譯」並附現有 `services` 簽名；P6 第 2 項改成「`Payment` 已存在，只缺 `fulfillment_status` ＋ 真實失敗路徑」；P6 新增重複索引與 `int(total)` 點數兩項小債；P8 菜單新增 `.env` 引號／空白解析差異與死變數兩項；缺檔清單只剩 `users/models.py`、Python 版本、Postgres 版本。
- **Verification Level**: **L1**（全部依據都是真碼這件事屬實；但第 8 項明確標為待驗，且一行 API 程式碼仍未寫）
- **Gate Impact**: P5 預算 1.5 → 1 段；P8 風險上升（`.env` 解析差異是新增的真失敗面）；P1–P5 約 7.5 段。目前仍卡在 P1.0，已完成 0 段，真踩 0 項。
- **Priority**: High
- **Status**: Processed

---

## Record 37 — 六份模板到位 ＋ 舊改善計劃書併入 v2.3

- **Date**: 2026-08-28 14:29
- **Trigger**: 學習者上傳 `shop-improvement-plan.canvas.tsx`（舊清單，46 項／九類）並要求併成 v2.3；同時上傳六份模板（`product.html` 55 KB、`product_list.html`、`carts_list.html`、`checkout.html`、`success.html`、`failed.html`）。
- **Issue Description**:
  1. **舊清單判錯一項，我上一輮也差點跟著錯**。舊清單第 1 條「購物車減少無效」不成立：`carts_list.html` 的「−」是 POST form 帶 `quantity=-1`，`cart.py:31` 是 `+= quantity` → 減少有效。**真問題是下界只由模板 `{% if item.quantity > 1 %}` 守，後端零驗證**。教訓：不要在沒有模板的情況下對前後端互動下結論；上一輮我已正確標為待驗（`grep -rn carts:add templates/`），這次模板到手即結案。
  2. **新發現四項紅級真 bug（舊清單全部沒抓到）**：
     - **無貨哨兵大小寫不符**：`product.html:138` value=`Out-of-stock`（JS 第 770 行也是大寫）vs `carts/views.py:49` `sku == 'out-of-stock'` → 守門永不成立 → `get_object_or_404(sku='Out-of-stock')` → **選缺貨尺寸得到 404而非提示**。
     - **related products 傳錯 ID**：`product.html:522` `<a href="{% url 'carts:add' item.id %}">`，`item` 是 Product，但 `carts:add` 收 `variant_id`。且是 GET。
     - **數量欄 `<input type="text" name="demo_vertical2">`** ＋ `int()` 無 try/except → `abc` 就 500。
     - **checkout modal 可重複提交**：`<button type="submit" form="checkout-form">` 無 disable、無冕等鍵 → 冕等缺口從理論升為實證。
  3. **模板逆推出契約級修正（本輮最有價值的部分）**：P1.2 必須支援 `category`／`q`／`min`／`max`／`page` 五參數；P1.1 分類需 `total_product_count`／`sub_product_count`／`sub_categories`（且必須 annotate）；P1.3 需 `current_variant`／`current_color_variants` 並以布林 `in_stock` 取代字串哨兵；P5 請求體對齊 `CheckoutForm` 七欄；**409 body 沿用 `failed.html` 的 `reason`／`items[{product,requested,available}]`**；201 body 對齊 `success.html` 顯示欄位。
  4. **舊清單的商業眼光優於我的清單**：`Order` 金額拆欄（`shipping_fee`／`tax`／`discount_amount`）是我漏寫的，已升級為阻塞進 P6。反之舊清單完全沒有：履約（fulfillment）、營運後台權限（把 Django Admin 当客服台）、部署／環境紀律、驗證標準。
  5. **两整類作廢**：舊清單「自訂 Admin 強化」→ P7（Django Admin 無欄位級權限、無稽核日誌）；「React + DRF 整合順序」→ 已被 P1–P5 取代。測試三項歸 P5.5。
- **Suggested Revision**: 已實施。清單 v2.2 → **v2.3**（45,274 bytes，622 行）：新增 `p9-backlog` todo、舊 10 bug 重審表、八項新發現、模板契約補充、六項升級阻塞、P9 全文保留（P9-A–P9-I）、v2.3 變更記錄 8 條。已改用行號＋`find_one()` 斷言腳本（`/data/patch_v23.py`），五項錮點全中，沒重蹈 `editFile` 字串比對的覆轍。
- **Verification Level**: **L1**（模板原文行號可引；但契約尚未被任何真實請求打過）
- **Gate Impact**: **零**。併一份清單不是進度。P1.0 的 `curl -i /api/v1/` 仍為 404，已完成段數仍為 0，真踩 0 項。P9 不計入 P1–P5 的 7.5 段預算。
- **Priority**: High
- **Status**: Processed

---

## Record 38 — 框架回寫：`system.md` ＋ `teacher-persona.md` → v4.1

- **Date**: 2026-08-29 10:42
- **Trigger**: 學習者追問「system 和 teacher-persona 不需要改嗎？」—— 正確，上一輮只改了 checklist v2.3，三份框架檔進入不一致狀態。
- **Issue Description**（這是一筆流程缺失，不是知識缺失）:
  1. **W6「Checklist Sync」只寫了 checklist，沒有規定反向回寫**。v2.3 把 `P4` 的工作量推大、新增 `P9`、把六項升為阻塞，但 `system.md` 的段數工作單、Repo Ground Truth、Why-Bank 全部停在模板到齊之前。兩份檔互相矛盾時，下一輮開工就會押錯閘門。
  2. **教學素材浪費**。六份模板採出的五個真 bug（大小寫哨兵、前端當驗證、沉默 False、傳錯 id、重複提交）是現成的第一性原理教案，不進 persona 的三欄表就只能靠臨場想起。
  3. **誤判本身沒被制度化**。「購物車減少無效」這筆誤判已在 Record 37 記下，但当時沒有變成一條規則，等於允許它再發生一次。
- **Suggested Revision**: 已實施。`system.md` → v4.1（26,013 bytes / 322 行，14 筆修改）：Scope Lock 6–7、Ground Truth 五列、`P4` 1.5→2`P6` 2–32→3、新增 `P9` 列、`P1`–`P8` 合計 11.5 段、Constraints 13–15、Verification 加「模板事實是 L1」、Why-Bank 加九題、File Reference 加舊 canvas 不再讀、Change Log。`teacher-persona.md` → v4.1（24,681 bytes / 274 行，5 筆）：Creed 7–8、黑色幽默六則、三欄表七列、Catchphrases 四句。
  - **最重要的一條是 Constraint 15**：對前後端接縫下判斷前必須 `grep -rn templates/`。這條規則的成本是一次公開誤判，便宜。
  - **新增流程紀律**：今後 checklist 每次改版，同一輮必須檢查三點 —— 段數工作單、Repo Ground Truth、Why-Bank；有新 bug 型態則進 persona 三欄表。
- **Verification Level**: **L2**（三份檔已一致且斷言全中；但框架的教學效果要等 `P1.0` 真踩之後才能判 L3）
- **Gate Impact**: **零**。改框架不是進度。預算因本輮重算而從 11 段升到 **11.5 段**（`P4` ＋0.5），`P6` 從 2–3 收緊為 3。已完成段數 0，真踩 0，`curl -i /api/v1/` 仍未跑。
- **Priority**: Medium
- **Status**: Processed

---

## Record 39 — P1.0 #1 自證寫錯：OPTIONS 預檢不會因為 middleware 排後就掉 ACAO

- **Date**: 2026-08-29
- **Trigger**: 學習者真踩 P1.0 #3（拿掉 `include` → DEBUG 404 頁，patterns 沒有 `api/v1/`）；同時 Postman `OPTIONS /api/v1/` 帶 `Origin: http://localhost:5173` 仍回 200 且有 `access-control-allow-origin`。當時 `CorsMiddleware` 已在 `CommonMiddleware` **之後**。
- **Issue Description**: 上一輪把 #1 的一行自證寫成「把 `CorsMiddleware` 挪到 `CommonMiddleware` 後面 → OPTIONS 的 `Access-Control-Allow-Origin` 消失」。這是錯的。`django-cors-headers` 對預檢（`OPTIONS` + `Origin` + `Access-Control-Request-Method`）由 `CorsMiddleware` **自己回 200**，不經過 view、也不需要 URL 掛得上。所以：(1) `include` 拿掉時 GET 404、OPTIONS 仍 200＋ACAO；(2) middleware 排在 `Common` 後面，OPTIONS 照樣有 ACAO。真正會被 `CommonMiddleware` 截走、讓 `CorsMiddleware` 沒機會跑 `process_response` 的，是 **無尾斜線的 GET**（`APPEND_SLASH` 的 301）。Postman 預設跟著轉址，會直接看到第二次請求（有斜線）的 200＋header，把第一次 301 沒 header 的證據吃掉。
- **Suggested Revision**: P1.0 #1 自證改為：Postman 關閉 Follow Redirects → `GET http://127.0.0.1:8000/api/v1`（無尾斜線）＋ header `Origin: http://localhost:5173`。排錯：301、沒有 `Access-Control-Allow-Origin`。排對：301、有這顆 header。做完立刻把 `CorsMiddleware` 修回 `SecurityMiddleware` 正下方。
- **Verification Level**: **L3**（#3 有真實 404 HTML）；#1 仍 **L0**（自證指令已改，尚未用無尾斜線 301 跑過）
- **Gate Impact**: P1.0 閘門已綠（先前 `GET /api/v1/` → 200 `{}`）。試錯覆蓋率 1/6。通關仍差 #1（或任一第二項）。
- **Priority**: High
- **Status**: Processed

---

## Record 40 — P1.0 通關：閘門 200 + 試錯 #3／#1

- **Date**: 2026-08-29
- **Trigger**: 學習者補上 #1 對照：同一條 `curl -sD - -o /dev/null -H "Origin: http://localhost:5173" http://127.0.0.1:8000/api/v1`（無 `-L`）。壞順序：301、無 ACAO。`CorsMiddleware` 移回 `SecurityMiddleware` 下方後：301、`access-control-allow-origin: http://localhost:5173`、`Vary: origin`。
- **Issue Description**: P1.0 閘門先前已綠（`GET /api/v1/` → 200 `{}`）。#3 已於同日入帳。#1 證明 header 是在 **response 回程** 貼的（`process_response`）：`CommonMiddleware` 截走 request 時，後面的 middleware 沒進堆疊。Postman 跟著轉址會把 301 吃成 200，不能當自證。
- **Suggested Revision**: P1.0 標 **L3 + 2/6 通關**。下一刀 **P1.1** `GET /api/v1/categories/`（樹、只 `is_active`、計數用 annotate）。`p1-catalog-api` 維持 `in_progress`。
- **Verification Level**: **L3**
- **Gate Impact**: P1.0 關。已完成 0.5／11.5 段。未綠閘門改為 P1.1（樹狀 JSON + 查詢數不隨分類數暴增）。
- **Priority**: High
- **Status**: Processed

---

## Record 41 — 學習者下令：不准擅自寫代碼；只准改清單與 rules

- **Date**: 2026-08-29
- **Trigger**: 學習者在 P1.0 #1 對照齊之後明確下令：「你只能更新列表和 rules 的檔案，你不能擅自作主寫代碼。」觸發點是上一輪教師未經要求就把 `config/settings.py` 的 `MIDDLEWARE` 修回對的順序。
- **Issue Description**: 「Code First」被執行成「Agent 直接改 repo」。學習者要自己貼碼、自己踩錯；教師搶寫等於沒收鍵盤。對照實驗的「修回」那一步也該由他做，教師只出可貼的區塊。
- **Suggested Revision**: 已寫入 `system.md` v4.2 Scope Lock 8 ＋ Constraint 16，以及 `teacher-persona.md` Interaction Rule 11。預設可改：`shop-rebuild-checklist.md`、`.cursor/rules/*`。應用程式碼（`config/`、apps、`requirements.txt`、templates、`frontend/`）未聽到「寫進檔／幫我改」一律不准動。
- **Verification Level**: **L2**（規則已落地；下一輪 P1.1 若教師又直接寫 `serializers.py` 則本記錄失效）
- **Gate Impact**: 無閘門。P1.0 維持 L3 通關。教學流程變更：之後出碼只在對話。
- **Priority**: High
- **Status**: Processed

---

## Record 42 — P1.1 閘門綠；Postman 為 API 手測首選

- **Date**: 2026-08-30
- **Trigger**: 學習者修完 typo 鏈後 `curl` 與 shell 皆通過；要求之後盡量用 Postman 測 API。
- **Issue Description**: 閘門：`GET /api/v1/categories/` 樹狀 2 根；shell `200 1`。P1.1 菜單 0/4，標 L3（脆）。
- **Suggested Revision**: 清單／`system.md` 已同步。下一刀 P1.2。
- **Verification Level**: **L3**
- **Gate Impact**: P1.1 關。已完成 1.0／11.5 段。blocking → P1.2。
- **Priority**: High
- **Status**: Processed

## Record 43 — 教學格式改版 v4.3：逐單位講解協定（學習者回報「一次出太多概念」）

- **Date**: 2026-08-30
- **Trigger**: 學習者貼回 P1.2 那一輪的輸出，指出「一次出太多概念，令我感到混亂和迷惑」，並定義想要的形狀：先說接下來要做什麼 → 為什麼要建／改這個檔案、它負責什麼 → 每個 class／function 負責什麼 → 每一行的功能、細節、不這樣寫會出什麼錯 → 一個 class 內多個 function 逐一講 → **講解完才貼那一段代碼**。
- **Issue Description**: 根因是兩條互相擠壓的舊規則，不是單純的臨場失手。`system.md` W2 要求「一輪一個檔案或一個函式，貼**完整**可貼上的碼」，`teacher-persona.md` Expression Style 又限制「散文每輪 ≤8 行」。結果：碼被迫整檔一次倒出，解釋被迫壓成 8 列設計決策表 ＋ 5 列參數表 ＋ 4 列菜單，而且三張表全部排在學習者看到任何一行碼之前。同一輪還混進 typo 修正、view、`api_urls.py`、`REST_FRAMEWORK` 四件事。
- **Suggested Revision**:
  - `system.md` → v4.3（12 筆，27,333 → 31,950 B）：W2 整段改寫為「逐單位講解協定」七步（接下來做什麼／檔案卡／單位卡／逐行講解／碼／菜單≤2／停）；碼從最先移到講解之後。Constraint 2 改為逐行為什麼；Constraint 4 菜單上限 3–5 → 2；新增 Constraint 17（一輪一單位）、18（概念預算 3）、19（碼前不准出決策表）。W0 加第 6 項單位清單；W3 菜單上限同步；Error Menu Format 的「沉默失敗／症狀不對稱」改為每個 P 階段各至少一次；W5 筆記第 3 格改成逐行表；新增指令 `/繼續` `/慢` `/單位` `/整檔`。
  - `teacher-persona.md` → v4.3（13 筆，25,244 → 30,917 B）：The Shape of Every Turn 六拍 → 七拍且碼移到第 5 拍；新增 Personality 8「Pacer」（主動喊停）；Interaction Rules 1–3 改寫，新增 12（一輪一單位）、13（不准先貼整檔、不准碼前決策表）；Expression Style「散文 ≤8 行」廢除，改為概念密度上限；Example Turn 1／2 降為反面教材並附診斷，新增 Example Turn 3 作為七拍正面示範。
- **Verification Level**: **L1**（規則文字已落地並通過唯一命中／行號定位斷言；實際教學效果要等 P1.2 逐單位跑完才算 L2）
- **Gate Impact**: 零。不動 repo、不動閘門定義、不動段數預算（`P1`–`P8` 仍 11.5 段）。P1.2 拆成 7 個單位推進。
- **Priority**: High
- **Status**: Processed

### 附註：本次 patch 的技術教訓

第一版 `patch_v43.py` 用「多行逐字比對」替換 persona 的 `## The Shape of Every Turn` 整段，`count=0` 直接失敗。原因是多行區塊的逐字比對對空白、全形符號、換行極度敏感，而需要比對的 needle 越長，命中率越低。改用 `patch_v43b.py` 的「**前綴定位行號 → 整段換掉**」（`repl_line` / `repl_block` / `insert_after`，各自斷言唯一命中）後 13 筆全中。腳本在失敗時 `sys.exit(1)` 且不寫檔，所以 persona 沒有被半套修改污染 —— 這個「全中才存檔」的性質要保留。

---

## Record 44 — P1.2 閘門綠（L3 脆）；學習者下令開 P1.3

- **Date**: 2026-08-30
- **Trigger**: 學習者 Postman／`curl` 貼回 P1.2 閘門輸出後，問「下階段是什麼」，並下令「直接開 P1.3」。隨後要求回寫 log 與 checklist。
- **Issue Description**:
  1. **閘門綠**：`GET /api/v1/products/` → `{count: 7, next: ?page=2, previous: null, results: [6]}`。`curl -s ... | jq '.count, (.results|length)'` 得到 `7`／`6`。`PAGE_SIZE: 6` 對得上。白名單只有 `id/name/slug/base_price/image/category`；`image` 是完整 URL。
  2. **落地檔（repo 已有）**：`products/serializers.py::ProductListSerializer`；`products/api_views.py::ProductListView.get_queryset`（`Product.active` ＋ `select_related('category')` ＋ `q`／`category`／`min`／`max` ＋ 搜尋 `.distinct()`）；`config/settings.py` `DEFAULT_PAGINATION_CLASS`／`PAGE_SIZE: 6`；`config/api_urls.py` `products/`。
  3. **試錯 0/6**。手測過好路徑與兩發非菜單：`?category=gg` → 404 `No Category matches the given query.`；`?q=blue` → 200 空集合（庫裡顏色是 `32 BEIGE`／`09 BLACK`／`69 NAVY` 等，沒有 `blue`）。`?q=XL` 回 `id` 7 與 3 各一次——`3XL` 被 `icontains` 命中。現庫每件商品約 1 列 variant，菜單 #3（沒 `distinct()` 會重複列）用現資料踩不到。學習者選擇不補菜單、直接開 P1.3。依通關規則標 **L3（脆）**，`p1-catalog-api` 維持 `in_progress`。
  4. **教學筆記（不入菜單總帳）**：五個 query 一次全開會互相蓋掉；`category` 填商品 slug（`v-neck-t-shirt`）不是分類 slug（`tshirts`）→ 直接 404。
  5. **P1.3 已開工、未綠**。對話已出詳情四個 serializer（`final_price`、`in_stock`、`current_variant`／`current_color_variants`）。repo `products/serializers.py` 仍停在 `ProductListSerializer`；import 出現 `ProuductImage` typo。尚無 `ProductDetailView`、尚無 `{slug}/`。
- **Suggested Revision**: 清單 P1.2 標閘門綠／L3（脆）／0/6；P1.3 標已開工、閘門未綠；repo 現況列改成 DRF 已裝、`api/v1/` 已掛列表。`system.md` Ground Truth 同步。下一刀 `ProductDetailView`（`lookup_field = 'slug'`）。
- **Verification Level**: **L3**（P1.2 閘門有真實 JSON／curl）；試錯覆蓋率 0/6 → **脆**。P1.3 **L0**（對話有碼，repo 未貼、端點未掛）。
- **Gate Impact**: P1.2 關。已完成 2.0／11.5 段。blocking → P1.3。
- **Priority**: High
- **Status**: Processed

---

## Record 45 — P1.3 閘門綠（L3 脆）；P1 全段完成；Git 分支已 push

- **Date**: 2026-08-31
- **Trigger**: 學習者逐單位完成 P1.3（serializer 四件＋`ProductDetailView`＋`{slug}/`），貼回 `curl`／`jq` 閘門輸出與 404 邊界；修 `SIZES_LIST`；開分支 commit 並 push；下令更新 log 與 checklist。
- **Issue Description**:
  1. **P1.3 閘門綠**：`GET /api/v1/products/sweat-oversized-pullover-hoodie/` → 200 JSON。`variants`／`images` 皆為陣列；`variants[0].price`=`"49.90"`（非 null）；`in_stock`=false（stock=0，契約正確）。`current_variant`／`current_color_variants` 齊。`jq` 摘要：`variant_count=1`、`image_count=1`。
  2. **404 邊界**：`this-slug-does-not-exist` → 404 `No Product matches the given query.`；`/products/1/` → 404（slug lookup，非 pk）。
  3. **落地檔（repo）**：`products/serializers.py` 全 serializer 鏈；`products/api_views.py::ProductDetailView`（`lookup_field='slug'`，`prefetch_related`）；`config/api_urls.py` `products/<slug:slug>/`；`products/views.py` `SIZES_LIST` 改 `('XS','S','M','L','XL','2XL','3XL')`。
  4. **試錯 0/5**（P1.3 菜單未踩）→ **L3（脆）**。P1 整段：P1.0 2/6；P1.1 0/4；P1.2 0/6；P1.3 0/5——閘門皆綠，試錯總覆蓋偏低。
  5. **Git**：本地曾 typo 分支 `feature/pq-catalog-api`，已 rename `feature/p1-catalog-api`；commit `99e1b8d` `Add P1 catalog read-only API…` 已 push `origin/feature/p1-catalog-api`；`main` 未 merge。
  6. **教學筆記（不入菜單總帳）**：shell 改 `serializers.py` 後須 `exit()` 重開，否則 `ImportError`（舊 module 緩存）。`?color=` 手測勿用占位符 URL。學習者問 `ProductImageSerializer` 為何不吐 `product`——詳情嵌套下父層已是 product。
- **Suggested Revision**: 清單 v2.5：P1.3 綠／P1 todo completed；repo 現況＋Git；blocking → P2。`system.md` Ground Truth 同步。試錯總帳加 P1.3 0/5。下一刀 P2.0（`frontend/` 腳手架）。
- **Verification Level**: **L3**（真實 curl JSON + 404）；試錯 0/5 → **脆**
- **Gate Impact**: P1.3 关；**P1 全段关**。已完成 **2.5**／11.5 段。blocking → **P2**
- **Priority**: High
- **Status**: Processed

---

## Record 46 — P2 閘門綠（L3 脆）；blocking → P3

- **Date**: 2026-09-02
- **Trigger**: 學習者在 `:5173` 跑通列表＋詳情後宣告「閘門過了」，下令更新 log 與 checklist。
- **Issue Description**:
  1. **P2 閘門綠**：Vite `http://localhost:5173/` 列出真商品；詳情頁從 `current_color_variants` 對出 `variant.id`，畫面與 `console.log('variant_id', …)` 同步。契約只讀 P1 三端點，不加購。
  2. **落地檔**：`frontend/`（Vite＋React＋`react-router-dom`）；`frontend/.env` `VITE_API_URL=http://127.0.0.1:8000/api/v1`；`src/api/client.js`（`apiFetch` 檢查 `response.ok`；`getProducts`／`getProduct`）；`pages/ProductListPage.jsx`；`pages/ProductDetailPage.jsx`；`App.jsx` `Routes`（`/`、`/products/:slug`）；`main.jsx` `BrowserRouter`。
  3. **試錯 1/5**：菜單 #1 真踩（假 slug → `API 404: No Product matches…`，證明只寫 `.catch` 接不到 HTTP 錯誤）。#2–#5 未踩 → **L3（脆）**。
  4. **手測／typo（不入菜單總帳）**：`getProduct` 誤 import 進列表 → `getProducts is not defined`；`singnal`／`signal` 拼錯 → 列表「错误：signal is not defined」；`ignore` 未宣告；`:8000/?category=sweaters` 是 Django 模板，不會印 `variant_id`。學習者問列表為何不像模板——P2 閘門是資料通路，不是 Pixio 還原。
  5. **Git**：P1 仍在 `feature/p1-catalog-api` @ `99e1b8d`；`frontend/` 當時多半尚未 commit。
- **Suggested Revision**: 清單 v2.6：P2 綠／`p2-storefront` completed；repo 現況含 `frontend/`；blocking → P3。`system.md` Ground Truth 同步。試錯總帳加 P2 1/5。下一刀 P3.0（csrf／login）。
- **Verification Level**: **L3**（學習者宣告閘門過；對話有 `:5173` 列表錯誤畫面與 404 試錯）。試錯 1/5 → **脆**
- **Gate Impact**: P2 關。已完成 **4.5**／11.5 段。blocking → **P3**
- **Priority**: High
- **Status**: Processed

---

## Record 47 — P3 閘門綠（L3 通關）；blocking → P4

- **Date**: 2026-09-03
- **Trigger**: 學習者完成 `accounts/api_views.py` 四端點、`config/api_urls.py` auth 路由；Postman 五步序列通過；下令更新 checklist／revision log 並 git commit。
- **Issue Description**:
  1. **P3 閘門綠（Postman）**：`GET /api/v1/csrf/` → 200；`POST /auth/login/` → 200 `{id, username}`；`GET /me/` → 200 `{id, username, email}`；`POST /auth/logout/` → 200；`GET /me/` → 403 `Authentication credentials were not provided.`
  2. **落地檔**：`accounts/api_views.py`（`csrf_view`、`api_login`、`api_logout`、`me_view` + DRF `IsAuthenticated`）；`config/api_urls.py` 四條 auth path；`config/settings.py` 沿用 P1.0 的 `SessionAuthentication`／`CORS_ALLOW_CREDENTIALS`。
  3. **試錯 3/5 + 手測 2 項**：註解 `@permission_classes` → AnonymousUser 進 body → 500；POST 帳密到 `/me/` 而非 `/auth/login/` → 403；GET logout → 405；`Client` → `DisallowedHost: testserver`（改 `RequestFactory`）。`api_logout` shell 驗證：`before _auth_user_id=2` → `after None`。
  4. **未做（不擋後端閘門）**：`frontend/src/api/client.js` 尚未加 `credentials: 'include'` 與 login 流程；瀏覽器仍可能「Postman 綠、:5173 脆」。
  5. **Git**：分支 `main`；本次 commit 含 P3 程式碼 + checklist v2.7 + Record 47。`frontend/` 仍可能未 commit。
- **Suggested Revision**: 清單 v2.7：`p3-auth` completed；repo 現況 + P3 落地檔 + 試錯總帳四行；blocking → P4。Statistics v2 更新。下一刀 P4.0 `carts/api_views.py`。
- **Verification Level**: **L3**（Postman 真實 status + JSON）；試錯 3/5 → **通關**
- **Gate Impact**: P3 關。已完成 **5.5**／11.5 段。blocking → **P4**
- **Priority**: High
- **Status**: Processed

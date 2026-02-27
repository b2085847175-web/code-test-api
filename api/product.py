from requests import session
from common.tool import get_headers


def get_products(token, shop_id="585", page=1, page_size=10, search=""):
    """
    获取店铺商品列表

    参数:
        token: 登录 token
        shop_id: 店铺ID，默认 585（儒意化妆品旗舰店）
        page: 页码，默认第1页
        page_size: 每页数量，默认10条
        search: 搜索关键词，默认为空

    返回:
        响应对象
    """
    url = "https://dev.zhiyan.chat/api/products/"
    params = {
        "page": page,
        "pageSize": page_size,
        "search": search,
        "shop_id": shop_id
    }
    headers = get_headers(token)
    return session().get(url=url, params=params, headers=headers)


def get_product_by_index(token, shop_id="585", index=0, page=1, page_size=10):
    """
    获取店铺商品列表中指定索引的商品，返回 inquiry_product 格式

    参数:
        token: 登录 token
        shop_id: 店铺ID，默认 585
        index: 商品在列表中的索引，默认第0个
        page: 页码，默认第1页
        page_size: 每页数量，默认10条

    返回:
        dict: 商品信息，格式为 {"id": "...", "title": "...", "url": "..."}
        如果获取失败或索引越界，返回 None
    """
    response = get_products(token, shop_id, page, page_size)
    result = response.json()

    if result.get('code') != 200:
        print(f"获取商品列表失败: {result.get('message')}")
        return None

    items = result.get('result', {}).get('data', [])
    if index >= len(items):
        print(f"索引 {index} 越界，商品列表共 {len(items)} 条")
        return None

    product = items[index]
    return {
        "id": str(product.get('product_id', '')),
        "title": product.get('product_title', ''),
        "url": f"https://item.taobao.com/item.htm?id={product.get('product_id', '')}"
    }


def list_products_brief(token, shop_id="585", page=1, page_size=10):
    """
    打印店铺商品列表摘要，方便选择商品

    参数:
        token: 登录 token
        shop_id: 店铺ID
        page: 页码
        page_size: 每页数量

    返回:
        list: 商品列表
    """
    response = get_products(token, shop_id, page, page_size)
    result = response.json()

    if result.get('code') != 200:
        print(f"获取商品列表失败: {result.get('message')}")
        return []

    items = result.get('result', {}).get('data', [])
    total = result.get('result', {}).get('total', 0)

    print(f"\n店铺商品列表（共 {total} 条，当前第 {page} 页，每页 {page_size} 条）")
    print(f"{'='*60}")
    for i, item in enumerate(items):
        print(f"  [{i}] ID: {item.get('product_id')}  标题: {item.get('product_title')}")
    print(f"{'='*60}")

    return items


def get_product_by_id(token, shop_id="585", product_id="", max_pages=3, page_size=20):
    """
    根据商品ID获取商品信息，返回 inquiry_product 格式

    参数:
        token: 登录 token
        shop_id: 店铺ID，默认 585
        product_id: 商品ID（字符串或数字）
        max_pages: 最多搜索多少页，默认3页
        page_size: 每页数量，默认20条

    返回:
        dict: 商品信息，格式为 {"id": "...", "title": "...", "url": "..."}
        如果未找到商品，返回 None
    """
    if not product_id:
        print("商品ID不能为空")
        return None

    product_id_str = str(product_id)

    for page in range(1, max_pages + 1):
        response = get_products(token, shop_id, page=page, page_size=page_size)
        result = response.json()

        if result.get('code') != 200:
            print(f"获取商品列表失败: {result.get('message')}")
            return None

        items = result.get('result', {}).get('data', [])
        if not items:
            break

        for item in items:
            if str(item.get('product_id', '')) == product_id_str:
                print(f"已找到商品: [{product_id_str}] {item.get('product_title')}")
                return {
                    "id": product_id_str,
                    "title": item.get('product_title', ''),
                    "url": f"https://item.taobao.com/item.htm?id={product_id_str}"
                }

    print(f"未找到商品ID: {product_id_str}（已搜索 {max_pages} 页）")
    return None

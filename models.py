class Category:
    last_id = 0

    def __init__(self, name: str, url: str,img_url=None, parent_category_id: int = None):
        self.parent_category_id = parent_category_id
        self.img_url = img_url
        self.id = Category.last_id + 1
        self.name = name
        self.url = url

        Category.last_id = self.id


class Product:
    last_id = 0

    def __init__(self, name: str, category_id: int, url: str, price: str = None):
        self.name = name
        self.id = Product.last_id + 1
        Product.last_id = self.id
        self.category_id = category_id
        self.price = price
        self.url = url

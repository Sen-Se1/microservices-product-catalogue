from fastapi import HTTPException, status


class ProductException(HTTPException):
    pass


class ProductNotFound(ProductException):
    def __init__(self, detail: str = "Product not found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )


class ProductAlreadyExists(ProductException):
    def __init__(self, detail: str = "Product already exists"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail
        )


class InsufficientStock(ProductException):
    def __init__(self, detail: str = "Insufficient stock"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )


class InvalidPrice(ProductException):
    def __init__(self, detail: str = "Invalid price"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )
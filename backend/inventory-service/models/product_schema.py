from marshmallow import Schema, fields

class ProductAttributesSchema(Schema):
    """
    Esquema para los atributos de un producto.
    Define los campos que vienen del servicio de productos y el campo que añadimos.
    """
    id = fields.Int(dump_only=True, dump_default=0)
    name = fields.Str(dump_only=True, dump_default="")
    description = fields.Str(dump_only=True, dump_default="")
    price = fields.Str(dump_only=True, dump_default="0.00")
    is_active = fields.Int(dump_only=True, dump_default=0)
    created_at = fields.Str(dump_only=True, dump_default=None)
    updated_at = fields.Str(dump_only=True, dump_default=None)
    
    # --- CAMPO CLAVE ---
    # Aquí definimos explícitamente el campo que estamos añadiendo.
    available_stock = fields.Int(dump_only=True, dump_default=0)

class ProductSchema(Schema):
    """Esquema para un objeto de producto completo, siguiendo el formato JSON:API."""
    type = fields.Str(dump_only=True, dump_default="productos")
    id = fields.Str(dump_only=True, dump_default=None)
    attributes = fields.Nested(ProductAttributesSchema)

class ProductListResponseSchema(Schema):
    """Esquema para la respuesta completa de la lista de productos."""
    data = fields.Nested(ProductSchema, many=True)
    meta = fields.Dict()
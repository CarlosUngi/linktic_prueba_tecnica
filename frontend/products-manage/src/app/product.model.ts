// Interfaz para los atributos de un producto con stock
export interface ProductAttributes {
  id: number;
  name: string;
  description: string;
  price: string;
  is_active: number;
  created_at: string;
  updated_at: string;
  available_stock: number; // Campo añadido por el servicio de inventario
}

// Interfaz para un objeto de producto individual en el formato JSON:API
export interface ProductWithStock {
  id: string;
  type: string;
  attributes: ProductAttributes;
}

// Interfaz para la sección 'meta' de la respuesta
export interface JsonApiMeta {
  total: number;
  limite: number;
  offset: number;
}

// Interfaz para la respuesta completa de la API
export interface ApiResponse {
  data: ProductWithStock[];
  meta: JsonApiMeta;
}
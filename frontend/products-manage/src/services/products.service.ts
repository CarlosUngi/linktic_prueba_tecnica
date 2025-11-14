import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { ProductWithStock, CreateProductDTO, UpdateProductDTO } from '../models/product.model';

@Injectable({
  providedIn: 'root'
})
export class ProductsService {

  // La URL base utiliza el proxy configurado en proxy.json
  private apiUrl = '/product-services/api/v1/productos';

  // La API Key necesaria para las operaciones de escritura (POST, PUT, DELETE)
  // En un proyecto real, esto debería venir de una variable de entorno.
  private apiKey = 'my-secure-key-for-products-access-12345';

  constructor(private http: HttpClient) { }

  private getAuthHeaders(): HttpHeaders {
    return new HttpHeaders({
      'X-API-Key': this.apiKey
    });
  }

  createProduct(product: CreateProductDTO): Observable<{ data: ProductWithStock }> {
    return this.http.post<{ data: ProductWithStock }>(this.apiUrl, product, { headers: this.getAuthHeaders() });
  }

  updateProduct(id: number, product: UpdateProductDTO): Observable<{ data: ProductWithStock }> {
    return this.http.put<{ data: ProductWithStock }>(`${this.apiUrl}/${id}`, product, { headers: this.getAuthHeaders() });
  }

  deleteProduct(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${id}`, { headers: this.getAuthHeaders() });
  }

  getProduct(id: number): Observable<{ data: ProductWithStock }> {
    return this.http.get<{ data: ProductWithStock }>(`${this.apiUrl}/${id}`);
  }
}
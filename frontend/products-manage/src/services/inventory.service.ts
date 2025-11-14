import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { ApiResponse } from '../models/product.model';

@Injectable({
  providedIn: 'root'
})
export class InventoryService {

  // La URL base utiliza el proxy configurado en proxy.json
  private apiUrl = '/inventory-services/api/v1/inventory';

  constructor(private http: HttpClient) { }

  /**
   * Obtiene la lista de productos con su stock disponible.
   */
  getProductsWithStock(page: number, limit: number): Observable<ApiResponse> {
    const params = new HttpParams().set('page', page.toString()).set('limit', limit.toString());
    return this.http.get<ApiResponse>(`${this.apiUrl}/products-with-stock`, { params });
  }
}
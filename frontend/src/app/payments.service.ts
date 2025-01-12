import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

import { environment } from '../../environment';

@Injectable({
  providedIn: 'root'
})
export class PaymentService {
  public paymentsUrl = `${environment.apiUrl}/payments`;

  constructor(private http: HttpClient) {}

  getPayments(page: number, pageSize: number, search: string, sortOrder: string, filterStatus: string): Observable<any[]> {
    let params = new HttpParams()
      .set('page', page.toString())
      .set('page_size', pageSize.toString())
      .set('search', search)
      .set('filter_status', filterStatus)
      .set('sort_order', sortOrder);

    return this.http.get<any[]>(this.paymentsUrl, { params });
  }

  editPayment(paymentId: string, paymentData: any): Observable<any> {
    return this.http.put<any>(`${this.paymentsUrl}/${paymentId}`, paymentData);
  }

  downloadEvidence(paymentId: string) {
    const url = `${this.paymentsUrl}/${paymentId}/evidence`; 
    window.open(url);
  }

  uploadEvidence(paymentId: string, file: File): Observable<any> {
    const formData = new FormData();
    formData.append('evidence_file', file);
    return this.http.post<any>(`${this.paymentsUrl}/${paymentId}/evidence`, formData);
  }

  deletePayment(paymentId: string): Observable<any> {
    return this.http.delete<any>(`${this.paymentsUrl}/${paymentId}`);
  }
}
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { environment } from '../../environment';

@Injectable({
  providedIn: 'root'
})
export class PaymentService {
  private paymentsUrl = `${environment.apiUrl}/payments`;

  constructor(private http: HttpClient) {}

  getPayments(): Observable<any[]> {
    return this.http.get<any[]>(this.paymentsUrl);
  }

  downloadEvidence(paymentId: string) {
    const url = `${this.paymentsUrl}/evidence/${paymentId}`; 
    window.open(url);
  }
}
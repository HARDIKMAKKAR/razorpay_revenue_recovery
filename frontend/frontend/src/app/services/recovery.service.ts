import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Payment {
  id: string;
  customer: string;
  amount: number;
  failure_reason: string;
  payment_method: string;
  payment_gateway: string;
  attempt_number: number;
  customer_segment: string;
}

export interface RecoveryResult {
  failure_reason: string;
  amount: number;
  recommended_action: string;
  recovery_probability: number;
  expected_revenue: number;
  reason: string;

  alternatives: {
    action: string;
    recovery_probability: number;
    expected_revenue: number;
    action_cost: number;
    customer_friction: number;
  }[];
}

@Injectable({
  providedIn: 'root'
})
export class RecoveryService {

  private apiUrl =
    'http://localhost:5000/api/recovery';

  constructor(private http: HttpClient) {}

  recommend(payment: Payment): Observable<RecoveryResult> {

    const request = {
      amount: payment.amount,
      payment_method: payment.payment_method,
      payment_gateway: payment.payment_gateway,
      is_recurring: 1,
      attempt_number: payment.attempt_number,
      failure_reason: payment.failure_reason,
      customer_tenure_days: 500,
      total_transactions: 30,
      successful_transactions: 27,
      failed_transactions: 3,
      historical_success_rate: 0.90,
      avg_transaction_amount: 1500,
      days_since_last_success: 5,
      customer_segment: payment.customer_segment
    };

    return this.http.post<RecoveryResult>(
      `${this.apiUrl}/recommend`,
      request
    );
  }
}
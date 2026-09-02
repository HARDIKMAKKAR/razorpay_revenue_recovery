import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

import {
  RecoveryService,
  Payment,
  RecoveryResult
} from '../services/recovery.service';

@Component({
  selector: 'app-dashboard',
  standalone: true,

  // Required for *ngIf, *ngFor, number, percent, etc.
  imports: [CommonModule],

  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.css'
})
export class DashboardComponent {

  selectedPayment: Payment | null = null;
  recommendation: RecoveryResult | null = null;

  loading = false;

  payments: Payment[] = [
    {
      id: 'TXN001',
      customer: 'Rahul Sharma',
      amount: 5000,
      failure_reason: 'insufficient_funds',
      payment_method: 'UPI',
      payment_gateway: 'Razorpay',
      attempt_number: 1,
      customer_segment: 'regular'
    },
    {
      id: 'TXN002',
      customer: 'Ankit Kumar',
      amount: 1200,
      failure_reason: 'network_error',
      payment_method: 'UPI',
      payment_gateway: 'Razorpay',
      attempt_number: 1,
      customer_segment: 'new'
    },
    {
      id: 'TXN003',
      customer: 'Priya Singh',
      amount: 8500,
      failure_reason: 'bank_declined',
      payment_method: 'card',
      payment_gateway: 'Razorpay',
      attempt_number: 2,
      customer_segment: 'high_value'
    },
    {
      id: 'TXN004',
      customer: 'Aman Gupta',
      amount: 3200,
      failure_reason: 'expired_card',
      payment_method: 'card',
      payment_gateway: 'Razorpay',
      attempt_number: 1,
      customer_segment: 'regular'
    }
  ];

  constructor(
    private recoveryService: RecoveryService
  ) {}

  selectPayment(payment: Payment): void {

    this.selectedPayment = payment;
    this.recommendation = null;
    this.loading = true;

    this.recoveryService
      .recommend(payment)
      .subscribe({
        next: (result) => {
          this.recommendation = result;
          this.loading = false;
        },

        error: (error) => {
          console.error('Recommendation error:', error);
          this.loading = false;
        }
      });
  }

  formatFailure(reason: string): string {
    return reason
      .replace(/_/g, ' ')
      .replace(/\b\w/g, char => char.toUpperCase());
  }

  formatAction(action: string): string {
    return action
      .replace(/_/g, ' ')
      .replace(/\b\w/g, char => char.toUpperCase());
  }
}
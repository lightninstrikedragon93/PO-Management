export type RoleEnum = "requester" | "manager" | "it_rep" | "finance" | "admin";

export type POStatusEnum = 
  | "DRAFT" | "SUBMITTED" | "PENDING_MANAGER" 
  | "PENDING_IT" | "PENDING_FINANCE" | "APPROVED" 
  | "NEEDS_REWORK" | "INVOICED";

export type POCategoryEnum = "Services" | "Office Supplies" | "IT Equipment";

export interface User {
  id: number;
  email: string;
  role: RoleEnum;
  is_active: boolean;
}

export interface POLineItem {
  id?: number;
  po_id?: number;
  name: string;
  quantity: number;
  unit_price: number;
}

export interface PurchaseOrder {
  id: number;
  title: string;
  description?: string;
  category: POCategoryEnum;
  currency: string;
  total_amount: number;
  status: POStatusEnum;
  created_at: string;
  creator_id: number;
}
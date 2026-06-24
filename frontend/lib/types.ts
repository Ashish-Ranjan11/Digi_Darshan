export type Role = "pilgrim" | "admin" | "emergency_operator" | "scanner";

export type User = {
  id: number;
  name: string;
  email: string;
  phone?: string;
  role: Role;
  is_active: boolean;
};

export type Temple = {
  id: number;
  name: string;
  city: string;
  description?: string;
  max_capacity: number;
  current_occupancy: number;
  occupancy_percent: number;
  crowd_level: string;
  entry_gates: number;
  exit_gates: number;
};

export type Slot = {
  id: number;
  temple_id: number;
  start_time: string;
  end_time: string;
  capacity: number;
  booked_count: number;
  available_count: number;
  senior_reserved_capacity: number;
  is_active: boolean;
};

export type Booking = {
  id: number;
  temple_id: number;
  slot_id: number;
  ticket_code: string;
  visitor_count: number;
  senior_count: number;
  differently_abled_count: number;
  status: string;
  gate?: string;
  temple_name?: string;
  temple_city?: string;
  slot_start?: string;
  slot_end?: string;
};

export type Alert = {
  id: number;
  temple_id: number;
  title: string;
  message: string;
  severity: "info" | "warning" | "critical";
  status: "active" | "resolved";
  location?: string;
  instruction?: string;
  temple_name?: string;
  created_at: string;
};

export type ParkingZone = {
  id: number;
  temple_id: number;
  name: string;
  total_slots: number;
  available_slots: number;
  distance_label?: string;
  route_hint?: string;
};

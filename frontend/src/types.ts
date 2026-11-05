export interface ToolCall {
  name: string;
  arguments: Record<string, unknown>;
  result: Record<string, unknown>;
}

export interface Step {
  step: number;
  model: string | null;
  text: string | null;
  tool_calls: ToolCall[];
}

export type Kind = "benign" | "attack";

export interface Trial {
  id: string;
  model: string;
  config: string;
  case_id: string;
  kind: Kind;
  attack_family: string | null;
  repeat: number;
  canary: string | null;
  ticket_body: string;
  access_attempt: boolean;
  successful_read: boolean;
  confirmed_leak: boolean;
  task_complete: boolean;
  transcript: Step[];
}

export interface ConfigSummary {
  config: string;
  n_attacks: number;
  access_rate: number;
  read_rate: number;
  leak_rate: number;
  utility_rate: number;
  utility_n: number;
}

export interface FamilySummary {
  config: string;
  attack_family: string;
  n: number;
  read_rate: number;
  leak_rate: number;
}

export interface Bundle {
  generated_at: string;
  source: string;
  is_sample: boolean;
  configs: string[];
  config_descriptions: Record<string, string>;
  summary: {
    by_config: ConfigSummary[];
    by_family: FamilySummary[];
  };
  trials: Trial[];
}

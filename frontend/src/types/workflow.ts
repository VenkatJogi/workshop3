export interface WorkflowEvent { timestamp:string; event:string; agent?:string|null; message:string; metadata:Record<string,unknown> }
export interface AgentExecution { agent_name:string; status:string; duration_seconds?:number; revision_number:number; error?:string }
export interface Revision { agent_name:string; revision_number:number; previous_output:Record<string,unknown>; revised_output:Record<string,unknown>; reason:string; timestamp:string }
export interface AgentData { execution?:AgentExecution; output?:any; revisions?:Revision[] }
export interface WorkflowStatus {
  workflow_id:string; business_objective:string; status:string; revision_count:number;
  selected_agents:string[]; agent_executions:Record<string,AgentExecution>; events:WorkflowEvent[];
  file_validations:Array<{file_name:string;dataset:string;rows:number;status:string}>;
  data_summary?:any; plan?:any; critic_review?:any; revision_history:Revision[]; unresolved_issues:string[];
}
export interface ProductDecision { product_id:string; product_name:string; priority:string; recommended_action:string; reasoning:string; supporting_evidence:string[]; risks:string[]; estimated_business_impact:string }
export interface ActionItem { priority:string; action:string; owner?:string; timeline:string; expected_outcome:string }
export interface FinalResult { workflow_id:string; status:string; decision:{executive_summary:string;product_decisions:ProductDecision[];overall_strategy:string;key_tradeoffs:string[];confidence_score:number}; critic_review:any; action_plan?:{immediate_actions:ActionItem[];short_term_actions:ActionItem[];monitoring_actions:ActionItem[];business_summary:string}; revision_count:number; unresolved_issues:string[] }
export interface WorkflowForm { business_objective:string; demo_conflict_mode:boolean; useSample:boolean; inventory?:File; orders?:File; suppliers?:File }

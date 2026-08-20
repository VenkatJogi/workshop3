import type { AgentData, FinalResult, WorkflowForm, WorkflowStatus } from '../types/workflow'
const API=import.meta.env.VITE_API_URL||'http://localhost:8000'
async function json<T>(url:string,init?:RequestInit):Promise<T>{
  const res=await fetch(`${API}${url}`,init)
  if(!res.ok){const body=await res.json().catch(()=>({detail:res.statusText}));const detail=typeof body.detail==='string'?body.detail:body.detail?.message||JSON.stringify(body.detail);throw new Error(detail||'Request failed')}
  return res.json()
}
export const createWorkflow=(form:WorkflowForm)=>{
  if(form.useSample)return json<{workflow_id:string;status:string}>('/api/workflows/sample',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({business_objective:form.business_objective,demo_conflict_mode:form.demo_conflict_mode})})
  const body=new FormData();body.append('business_objective',form.business_objective);body.append('demo_conflict_mode',String(form.demo_conflict_mode));
  if(form.inventory)body.append('inventory',form.inventory);if(form.orders)body.append('orders',form.orders);if(form.suppliers)body.append('suppliers',form.suppliers)
  return json<{workflow_id:string;status:string}>('/api/workflows',{method:'POST',body})
}
export const getWorkflow=(id:string)=>json<WorkflowStatus>(`/api/workflows/${id}`)
export const getAgents=(id:string)=>json<Record<string,AgentData>>(`/api/workflows/${id}/agents`)
export const getResult=(id:string)=>json<FinalResult>(`/api/workflows/${id}/result`)
export const sampleUrl=(file:string)=>`${API}/api/sample-data/${file}`
export const wsUrl=(id:string)=>`${API.replace(/^http/,'ws')}/ws/workflows/${id}`

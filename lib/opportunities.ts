import seed from '@/data/opportunities.json';
import published from '@/data/published/opportunities.json';
import type {Opportunity} from '@/types/opportunity';
const all=((published as unknown[])?.length?published:seed) as unknown as Opportunity[];
export function getOpportunities():Opportunity[]{return all}
export function getOpportunity(slug:string){return all.find(x=>x.slug===slug)}
export function searchOpportunities(q:string,category?:string,status?:string){const s=q.toLowerCase().trim();return all.filter(o=>(!s||[o.title,o.summary,o.description,o.category,o.territory,...(o.beneficiaries||[])].join(' ').toLowerCase().includes(s))&&(!category||o.category===category)&&(!status||o.status===status))}
export function deriveStatus(opening:string|null,closing:string|null,permanent=false,exhausted=false,verified=true,now=new Date()){if(!verified)return 'PENDIENTE_DE_VERIFICACIÓN';if(exhausted)return 'AGOTADA';if(permanent)return 'PERMANENTE';if(opening&&new Date(opening)>now)return 'PRÓXIMA';if(closing&&new Date(closing)<now)return 'HISTÓRICA';if(opening&&new Date(opening)<=now&&(!closing||new Date(closing)>=now))return 'ABIERTA';return 'PENDIENTE_DE_VERIFICACIÓN'}

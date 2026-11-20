import raw from '@/data/opportunities.json';
export type Category = 'vivienda' | 'suministros' | 'fiscalidad' | 'oportunidades';
export type Opportunity = {
 id:string; slug:string; title:string; subtitle:string; category:Category; scope:string; region:string;
 status:'vigente'|'permanente'|'informativo'|'revision'|'cerrado'; statusLabel:string; amount:string; amountNote:string;
 audience:string; requirements:string[]; howTo:string; deadline:string; notes:string;
 sources:{name:string;url:string;type:string}[]; verifiedAt:string; reviewFrequency:string; confidence:'alta'|'media'|'baja'; editorialStatus:string;
};
export const opportunities = raw as Opportunity[];
export const categories = [
 {id:'vivienda',name:'Vivienda',description:'Compra, rehabilitación, eficiencia energética y acceso a vivienda.',icon:'⌂'},
 {id:'suministros',name:'Suministros',description:'Electricidad, gas, agua, conectividad y ahorro doméstico.',icon:'ϟ'},
 {id:'fiscalidad',name:'Fiscalidad',description:'Deducciones, bonificaciones y beneficios tributarios.',icon:'€'},
 {id:'oportunidades',name:'Oportunidades',description:'Programas, descuentos y convocatorias de interés.',icon:'✳'}
] as const;
export function getOpportunity(slug:string){return opportunities.find(x=>x.slug===slug)}
export function formatDate(date:string){return new Intl.DateTimeFormat('es-ES',{day:'numeric',month:'long',year:'numeric'}).format(new Date(date+'T12:00:00'))}

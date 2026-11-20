'use client';
import {useMemo,useState} from 'react';
import Link from 'next/link';
import type {Opportunity} from '@/lib/data';
const labels:Record<string,string>={vivienda:'Vivienda',suministros:'Suministros',fiscalidad:'Fiscalidad',oportunidades:'Oportunidades'};
export default function OpportunityExplorer({items}:{items:Opportunity[]}){
 const [category,setCategory]=useState('todas'); const [region,setRegion]=useState('todas'); const [query,setQuery]=useState('');
 const filtered=useMemo(()=>items.filter(x=>(category==='todas'||x.category===category)&&(region==='todas'||x.scope===region)&&(`${x.title} ${x.subtitle} ${x.audience} ${x.region}`).toLowerCase().includes(query.toLowerCase())),[items,category,region,query]);
 return <section className="explorer" id="oportunidades">
  <div className="section-head"><div><span className="eyebrow">CATÁLOGO DE OPORTUNIDADES</span><h2>Información que puede ayudarte a ahorrar</h2><p>Consulta las condiciones, comprueba si encajas y accede siempre a la fuente oficial.</p></div><span className="result-count">{filtered.length} resultados</span></div>
  <div className="filters"><label className="search-box"><span>⌕</span><input value={query} onChange={e=>setQuery(e.target.value)} placeholder="Buscar ayudas, descuentos o temas…" aria-label="Buscar oportunidades"/></label><select value={category} onChange={e=>setCategory(e.target.value)} aria-label="Filtrar por categoría"><option value="todas">Todas las categorías</option>{Object.entries(labels).map(([k,v])=><option key={k} value={k}>{v}</option>)}</select><select value={region} onChange={e=>setRegion(e.target.value)} aria-label="Filtrar por ámbito"><option value="todas">Todos los ámbitos</option><option value="España">España</option><option value="Cataluña">Cataluña</option></select></div>
  <div className="opportunity-grid">{filtered.map(item=><article className="opportunity-card" key={item.id}><div className="card-top"><span className="category-tag">{labels[item.category]}</span><span className={`status status-${item.status}`}>{item.statusLabel.split('·')[0]}</span></div><h3><Link href={`/ayudas/${item.slug}`}>{item.title}</Link></h3><p>{item.subtitle}</p><div className="amount">{item.amount}</div><div className="amount-note">{item.amountNote}</div><div className="card-bottom"><span>◷ Revisado: {new Date(item.verifiedAt+'T12:00:00').toLocaleDateString('es-ES')}</span><Link href={`/ayudas/${item.slug}`} className="text-link">Ver condiciones →</Link></div></article>)}</div>
  {filtered.length===0&&<div className="empty-state"><h3>No encontramos resultados</h3><p>Prueba con otra búsqueda o cambia los filtros.</p><button onClick={()=>{setCategory('todas');setRegion('todas');setQuery('')}}>Limpiar filtros</button></div>}
 </section>
}

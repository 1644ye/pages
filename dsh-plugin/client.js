window.__ModuleLoader__.load({id:'dsh-shopify-page-studio',factory(require){
  const React=require('react'),h=React.createElement;
  const PANEL='page-studio';
  function Workspace(){return h('div',{'data-page-studio-workspace':'',style:{height:'100%',minHeight:0,display:'flex',flexDirection:'column',background:'#f5f8ff',paddingTop:'var(--dsh-frame-top-clearance, 0px)'}},
    h('iframe',{src:'/page-studio/',title:'Shopify 页面工作台',style:{display:'block',flex:1,width:'100%',minHeight:0,border:0,background:'#f5f8ff'}}))}
  function PageIcon({size=18}){return h('svg',{width:size,height:size,viewBox:'0 0 24 24',fill:'none',stroke:'currentColor',strokeWidth:1.7,strokeLinecap:'round',strokeLinejoin:'round','aria-hidden':true},h('path',{d:'M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9Z'}),h('path',{d:'M14 3v6h6M8 13h8M8 17h5'}))}
  return {name:'page-studio',inject:['slots','layout'],apply(ctx){
    ctx.slots.inject('main',()=>ctx.slots.register({name:'main',key:PANEL},Workspace));
    ctx.slots.inject('sidebar.panellist',()=>ctx.slots.register({name:'sidebar.panellist',id:PANEL,order:20,label:()=> '页面工作台'},PageIcon));
  }};
}});

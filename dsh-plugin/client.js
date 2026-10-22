window.__ModuleLoader__.load({id:'dsh-shopify-page-studio',factory(require){
  const React=require('react'),h=React.createElement;
  function Workspace(){const[open,setOpen]=React.useState(false);return h(React.Fragment,null,
    h('button',{onClick:()=>setOpen(!open),style:{position:'fixed',bottom:24,left:24,zIndex:1200,padding:'10px 16px',borderRadius:8,background:'#314d37',color:'white',border:'1px solid #a9bba0'}},open?'关闭 Page Studio':'Page Studio · 页面生成'),
    open?h('div',{style:{position:'fixed',inset:'45px 35px 75px',background:'white',zIndex:1199,borderRadius:12,boxShadow:'0 15px 60px #0006',overflow:'hidden'}},h('iframe',{src:'/page-studio/',title:'DSH Shopify Page Studio',style:{width:'100%',height:'100%',border:0}})):null)}
  return {name:'page-studio',inject:['slots'],apply(ctx){ctx.slots.inject('shell.overlay',function*(){yield ctx.slots.register({name:'shell.overlay',id:'dsh-shopify-page-studio',order:900},Workspace)})}};
}});

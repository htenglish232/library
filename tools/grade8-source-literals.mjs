// Parse checked-in inline JavaScript, evaluate only isolated data initializers.
// No exam application or external script executes in the extractor.
import fs from 'node:fs';
import vm from 'node:vm';
import {parse} from 'acorn';
const source=fs.readFileSync(process.argv[2],'utf8'),out={variables:{},calls:[]};
// Node offsets below are relative to each inline script.
for(const match of source.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/gi)){
 const code=match[1];let ast;try{ast=parse(code,{ecmaVersion:'latest'});}catch{continue;}
 const value=node=>{try{return new vm.Script('('+code.slice(node.start,node.end)+')').runInNewContext({}, {timeout:100,contextCodeGeneration:{strings:false,wasm:false}});}catch{return undefined;}};
 const visit=node=>{
  if(!node||typeof node!=='object')return;
  if(node.type==='VariableDeclarator'&&['ObjectExpression','ArrayExpression'].includes(node.init?.type)){
   const result=value(node.init);if(result!==undefined)out.variables[node.id.name]=result;
  }
  if(node.type==='CallExpression'&&['renderResultCard','buildWordPool'].includes(node.callee.name))out.calls.push({name:node.callee.name,args:node.arguments.map(value),raw:code.slice(node.start,node.end)});
  for(const [key,v] of Object.entries(node))if(key!=='start'&&key!=='end'){if(Array.isArray(v))v.forEach(visit);else if(v&&typeof v==='object')visit(v);}
 };
 visit(ast);
}
process.stdout.write(JSON.stringify(out));

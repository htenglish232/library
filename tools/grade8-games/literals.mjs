// Read isolated JSON-like source literals; never execute the original application.
import vm from 'node:vm';
let input=''; for await(const chunk of process.stdin) input+=chunk;
const scripts=JSON.parse(input), result={};
function endLiteral(code,start){
 let depth=0,quote='',comment='';
 for(let i=start;i<code.length;i++){
  const c=code[i],next=code[i+1];
  if(comment==='line'){if(c==='\n')comment='';continue;}
  if(comment==='block'){if(c==='*'&&next==='/'){comment='';i++;}continue;}
  if(quote){if(c==='\\'){i++;continue;}if(c===quote)quote='';continue;}
  if(c==='/'&&next==='/'){comment='line';i++;continue;}
  if(c==='/'&&next==='*'){comment='block';i++;continue;}
  if(c==='"'||c==="'"||c==='`'){quote=c;continue;}
  if(c==='{'||c==='[')depth++;
  if(c==='}'||c===']'){depth--;if(depth===0)return i+1;}
 }
 throw Error('Unclosed literal');
}
for(const code of scripts){
 const re=/\b(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*(?=[{\[])/g;let match;
 while((match=re.exec(code))){
  try{
   const start=re.lastIndex,end=endLiteral(code,start),literal=code.slice(start,end);
   const value=vm.runInNewContext(`(${literal})`,{}, {timeout:500,contextCodeGeneration:{strings:false,wasm:false}});
   const encoded=JSON.stringify(value,(_,v)=>{if(typeof v==='function'||typeof v==='undefined')throw Error('Not static JSON');return v;});
   if(encoded.length>2)result[match[1]]=JSON.parse(encoded);
   re.lastIndex=end;
  }catch{/* Dynamic expressions are not guessed; adapters must report missing data. */}
 }
}
process.stdout.write(JSON.stringify(result));

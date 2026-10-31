export function studentEmail(id) {
  if(typeof id!=='string')throw Error('invalid-id');
  const normalized=id.trim().toUpperCase();
  if(!/^HT[A-Z0-9-]{4,30}$/.test(normalized))throw Error('invalid-id');
  return normalized.toLowerCase()+'@students.htenglish.invalid';
}
export function parseAssignment(search) {
  const params=new URLSearchParams(search);
  if([...params.keys()].some(k=>k!=='assignment')||params.getAll('assignment').length>1)throw Error('invalid-link');
  const id=params.get('assignment');
  if(id===null||id==='')return null;
  if(!/^[A-Za-z0-9_-]{1,64}$/.test(id))throw Error('invalid-link');
  return id;
}

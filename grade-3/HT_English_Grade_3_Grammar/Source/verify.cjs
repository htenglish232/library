
const fs = require('node:fs');
const path = require('node:path');
const {pathToFileURL} = require('node:url');
const assert = require('node:assert/strict');
const {chromium} = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const folder = path.join(__dirname,'../HTML_Output');
const all = JSON.parse(fs.readFileSync(path.join(folder,'manifest.json'),'utf8'));
const checked = [];
const chrome = process.env.CHROME_EXECUTABLE;

async function answer(page,q,value,mode){
  if(q.kind==='direct'){
    const input=page.getByRole('textbox',{name:q.id+' nhập trực tiếp',exact:true});
    await input.evaluate(el=>el.scrollIntoView({block:'center'}));
    if(mode==='practice'){
      await input.fill('x');
      assert(!(await page.locator('#feedback').isVisible()));
    }
    await input.fill('  '+String(value).toUpperCase().replaceAll("'",'’')+'  ');
    assert(!(await page.locator('#feedback').isVisible()));
    await input.press('Enter');
    return;
  }
  const label = q.kind==='match'?'chấm nối':q.kind==='word'||q.kind==='entry'||q.kind==='order'?'điền vào chỗ trống':value;
  const buttonName=q.original && q.kind==='match'?'Nối '+q.id:q.original && q.kind==='word'?q.id+' chọn từ':q.id+' '+label;
  const button=page.getByRole('button',{name:buttonName,exact:true});
  await button.evaluate(el=>el.scrollIntoView({block:'center'}));
  if(q.original)await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
  await button.click({timeout:4500});
  if(q.kind==='match'){
    const target=page.getByRole('button',{name:'Nối với '+value,exact:true});
    await target.evaluate(el=>el.scrollIntoView({block:'center'}));
    await target.click({timeout:4500});
  }else if(q.kind==='word'){
    const choice=page.locator('.menu').getByRole('button',{name:value,exact:true});
    if(q.original){
      try {
        await choice.click({timeout:550});
        return;
      } catch(error) {
        if(error.name!=='TimeoutError')throw error;
        await button.evaluate(el=>el.scrollIntoView({block:'center'}));
        await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
        if(!(await choice.isVisible()))await button.click({timeout:4500});
      }
    }
    await choice.click({timeout:4500});
  }else if(q.kind==='order'){
    let rest=value;
    while(rest){
      const enabled=await page.locator('.order-bank button:enabled').allTextContents();
      const token=enabled.sort((a,b)=>b.length-a.length).find(v=>rest===v||rest.startsWith(v+' '));
      assert(token,q.id+' missing token in '+rest);
      await page.locator('.order-bank button:enabled').getByText(token,{exact:true}).first().click({timeout:4500});
      rest=rest.slice(token.length).trimStart();
    }
    assert(!(await page.locator('#feedback').isVisible()));
    await page.locator('.menu').getByRole('button',{name:'Xác nhận',exact:true}).click({timeout:4500});
  }else if(q.kind==='entry'){
    const input=page.locator('.menu input');
    const viewport=page.viewportSize();
    if(viewport.width<500){
      const typed=value.slice(0,1);
      await input.fill(typed);
      await page.evaluate(()=>window.addEventListener('resize',()=>{
        document.body.dataset.entryResize='observed';
      },{once:true}));
      await page.setViewportSize({...viewport,height:viewport.height-320});
      try {
        await page.waitForFunction(()=>document.body.dataset.entryResize==='observed');
        assert(await input.evaluate(el=>document.activeElement===el),q.id+' lost focus on resize');
        assert.equal(await input.inputValue(),typed);
        assert(await page.locator('.menu').evaluate(el=>{
          const viewport=window.visualViewport;
          const {bottom,top}=el.getBoundingClientRect();
          return top>=viewport.offsetTop && bottom<=viewport.offsetTop+viewport.height;
        }),q.id+' entry menu left the visible viewport');
      } finally {
        await page.setViewportSize(viewport);
        await page.evaluate(()=>delete document.body.dataset.entryResize);
      }
    }
    await input.fill(value);
    await page.locator('.menu button').click({timeout:4500});
  }
}

(async () => {
  const browser = await chromium.launch({executablePath: chrome, args:['--allow-file-access-from-files']});
  try {
    for (const worksheet of all.filter(r=>r.generated && (!process.argv[2] || r.order>=Number(process.argv[2])) && (!process.argv[3] || r.order<=Number(process.argv[3])) && (process.argv[4]!=='untested'||!r.verification))){
      const errors=[];
      for (const viewport of [{width:1440,height:900},{width:390,height:844}]){
        const context=await browser.newContext({viewport,reducedMotion:'reduce'});
        const page=await context.newPage();
        const url=pathToFileURL(path.join(folder,worksheet.file)).href;
        page.on('pageerror',e=>errors.push(e.message));
        page.on('dialog',dialog=>dialog.accept());
        await page.goto(url);
        assert(await page.locator('#welcome').isVisible());
        await page.locator('#name').fill('Minh Anh');
        await page.locator('#cls').fill('3A');
        await page.locator('#teacher').fill('Cô Lan');
        await page.locator('#start').click();
        const choices = await page.evaluate(()=>QUESTIONS.map(q=>({id:q.id,page:q.page,kind:q.kind,ans:q.ans,choices:q.choices,opts:q.opts?.map(([v])=>v),group:q.group,original:typeof DATA==='undefined'})));
        const visited = new Set();
        const used = new Set();
        for (const q of choices){
          const options = Array.isArray(q.ans)?q.ans:[q.ans];
          const value = options.find(v=>!q.group||!used.has(v))||options[0];
          if(q.group)used.add(value);
          if(!visited.has(q.page)){
            await page.locator('[data-page="'+q.page+'"]').click();
            assert.equal(await page.locator('.page:visible').count(),1);
            await page.waitForFunction(()=>document.querySelector('.page:not([hidden]) img').naturalWidth>0);
            if(viewport.width>1000){
              const screenshot=await page.locator('.page:visible').screenshot({animations:'disabled'});
              fs.mkdirSync('work/qa',{recursive:true});
              fs.writeFileSync(path.join('work/qa',worksheet.label+'-'+(q.page+1)+'.png'),screenshot);
            }
            visited.add(q.page);
          }
          await answer(page,q,value,'practice');
          assert.equal(await page.locator('#feedbackTitle').innerText(),'✓ Chính xác! Em làm tốt lắm!',q.id);

        }
        const feedback=await page.locator('#feedbackText').innerText();
        await page.locator('[data-page="0"]').click();
        assert.equal(await page.locator('#feedbackText').innerText(),feedback);
        await page.locator('#nextPage').click();
        await page.reload();
        assert.equal(await page.locator('#count').innerText(),choices.length+'/'+choices.length);
        assert.equal(await page.locator('#pageStatus').innerText(),'Trang 2 / '+worksheet.pages);
        const manualSlots=await page.evaluate(()=>typeof DATA==='undefined'?[]:DATA.reviewSlots||[]);
        for(const slot of manualSlots){
          await page.locator('[data-page="'+slot.page+'"]').click();
          const input=page.getByRole('textbox',{name:slot.id+' giáo viên chấm',exact:true});
          await input.evaluate(el=>el.scrollIntoView({block:'center'}));
          await input.fill('Câu trả lời để giáo viên xem');
          await input.press('Enter');
        }
        if(manualSlots.length)await page.reload();
        await page.locator('#submit').click();
        assert.equal(await page.locator('.gradeInk').innerText(),'10');
        if(manualSlots.length)assert((await page.locator('#reportBody').innerText()).includes('Câu trả lời để giáo viên xem'));
        assert((await page.locator('#reportBody').innerText()).includes('Đúng: '+choices.length+' | Sai: 0 | Chưa làm: 0'));
        await page.locator('#report').evaluate(el=>el.scrollTop=el.scrollHeight);
        assert(await page.locator('.redGrade').isVisible());
        assert(await page.locator('.reportInfo').isVisible());
        await page.locator('#report>.action').click();
        await page.locator('#reset').click();
        assert(await page.locator('#welcome').isVisible());
        assert.equal(await page.locator('#name').inputValue(),'Minh Anh');
        await page.locator('[value="test"]').check();
        await page.locator('#start').click();
        const q=choices[0], value=Array.isArray(q.ans)?q.ans[0]:q.ans;
        await answer(page,q,value,'test');

        assert(!(await page.locator('#feedback').isVisible()));
        await page.locator('#submit').click();
        assert.equal(await page.locator('.gradeInk').innerText(),String(Number((10/choices.length).toFixed(1))).replace('.',','));
        assert.deepEqual(errors,[]);
        assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
        await context.close();
      }
      checked.push(worksheet.label);
      console.log(worksheet.label+' passed desktop and mobile');
    }
  } finally {
    await browser.close();
  }
})().catch(e=>{console.error(e);process.exitCode=1});

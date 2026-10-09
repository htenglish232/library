(() => {
  'use strict';
  const form = document.getElementById('account-form');
  const message = document.getElementById('account-message');
  const button = document.getElementById('create-submit');
  const download = document.getElementById('account-download');
  let url;
  function clearDownload() {
    if (url) URL.revokeObjectURL(url);
    url = null; download.hidden = true; download.removeAttribute('href');
  }
  form.addEventListener('input', clearDownload);
  form.addEventListener('submit', async event => {
    event.preventDefault(); clearDownload(); button.disabled = true;
    const password = document.getElementById('new-password');
    const confirm = document.getElementById('confirm-password');
    try {
      if (!window.crypto?.subtle || !window.HTTeacherCrypto) throw new Error('Hãy mở công cụ bằng trình duyệt mới qua HTTPS hoặc từ bản ZIP trên máy bạn.');
      if (password.value !== confirm.value) throw new Error('Hai lần nhập mật khẩu chưa giống nhau.');
      const file = document.getElementById('existing-accounts').files[0];
      if (file && file.size > 100000) throw new Error('Tệp tài khoản quá lớn. Vui lòng chọn đúng teacher-accounts.json.');
      let config = {schemaVersion: 1, accounts: []};
      if (file) {
        try { config = HTTeacherCrypto.validate(JSON.parse(await file.text())); }
        catch { throw new Error('Tệp tài khoản không đúng định dạng. Vui lòng kiểm tra tệp đã chọn.'); }
      }
      message.textContent = 'Đang tạo giá trị băm…';
      const username = document.getElementById('new-username').value;
      const account = await HTTeacherCrypto.create(username, password.value);
      config.accounts = config.accounts.filter(a => a.username !== username);
      config.accounts.push(account); HTTeacherCrypto.validate(config);
      url = URL.createObjectURL(new Blob([JSON.stringify(config, null, 2) + '\n'], {type: 'application/json'}));
      download.href = url; download.hidden = false;
      password.value = confirm.value = '';
      message.textContent = 'Tệp đã sẵn sàng. Nhấn liên kết tải bên dưới, rồi cập nhật tệp trên nhánh thử nghiệm.';
      download.focus();
    } catch (error) { message.textContent = error.message; }
    finally { button.disabled = false; }
  });
})();

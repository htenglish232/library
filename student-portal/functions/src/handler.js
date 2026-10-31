import {ApiError} from './service.js';
export function createHandler({auth, service}) {
  return async (req, res) => {
    res.set('Cache-Control', 'no-store');
    res.set('X-Content-Type-Options', 'nosniff');
    if (req.method === 'GET' && req.path === '/api/health') return res.json({service:'ht-student-portal', status:'ok'});
    try {
      if ((req.rawBody?.length || 0) > 65536 || Buffer.byteLength(JSON.stringify(req.body || {})) > 65536) throw new ApiError(413, 'payload-too-large');
      const token = /^Bearer (\S+)$/.exec(req.headers.authorization || '')?.[1];
      if (!token) throw new ApiError(401, 'sign-in-required');
      let user;
      try { user = await auth.verifyIdToken(token, true); } catch { throw new ApiError(401, 'sign-in-required'); }
      if (!user.uid || user.uid.includes('/')) throw new ApiError(401, 'sign-in-required');
      let result;
      if (req.method === 'GET' && req.path === '/api/dashboard') result = await service.dashboard(user.uid);
      else if (req.method === 'POST' && req.path === '/api/attempts/start') result = await service.start(user.uid, req.body);
      else if (req.method === 'POST' && req.path === '/api/attempts/submit') result = await service.submit(user.uid, req.body);
      else if (req.method === 'GET' && req.path === '/api/teacher/report') result = await service.teacherReport(user.uid, req.query.classId);
      else throw new ApiError(404, 'not-found');
      res.json(result);
    } catch (error) {
      // Never log request bodies, passwords, tokens or answers.
      res.status(error instanceof ApiError ? error.status : 500).json({error:error instanceof ApiError ? error.message : 'server-error'});
    }
  };
}

import api from './client';

/** POST multipart template batch; returns ZIP blob. */
export async function postTemplateBatch(formData: FormData): Promise<Blob> {
  const res = await api.post<Blob>('/generate/template-batch', formData, {
    responseType: 'blob',
    transformRequest: [
      (data, headers) => {
        if (data instanceof FormData) {
          delete headers['Content-Type'];
        }
        return data;
      },
    ],
  });
  return res.data;
}

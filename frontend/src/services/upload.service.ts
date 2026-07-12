/** Image upload service — to be implemented in future phases. */

export const uploadService = {
  async uploadImage(_file: File): Promise<{ url: string }> {
    throw new Error('Upload service not implemented yet')
  },
}

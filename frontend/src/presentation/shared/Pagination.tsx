import { Pagination as MuiPagination, Stack, Typography } from '@mui/material';

interface Props {
  page: number;
  total: number;
  itemsPerPage: number;
  onChange: (page: number) => void;
}

export function Pagination({ page, total, itemsPerPage, onChange }: Props) {
  const pages = Math.ceil(total / itemsPerPage);
  if (!total || page > pages) return null;
  return (
    <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}
      sx={{ alignItems: 'center', justifyContent: 'space-between', mt: 3, pt: 2,
        borderTop: '1px solid #EEEAF3' }}>
      <Typography sx={{ color: 'text.secondary', fontSize: 12 }}>
        Mostrando {(page - 1) * itemsPerPage + 1}–{Math.min(page * itemsPerPage, total)} de {total} eventos
      </Typography>
      <MuiPagination count={pages} page={page} color="primary" shape="rounded"
        siblingCount={0} onChange={(_, value) => onChange(value)}
        getItemAriaLabel={(type, value, selected) => type === 'page'
          ? `${selected ? 'Página actual, página' : 'Ir a la página'} ${value}`
          : type === 'next' ? 'Ir a la página siguiente' : 'Ir a la página anterior'} />
    </Stack>
  );
}

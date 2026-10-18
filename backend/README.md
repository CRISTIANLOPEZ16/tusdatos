# Backend

La capacidad del evento esta determinada por la capacidad de sus sessiones, Se asumio que el son eventos de auditorios donde cada sesion tiene un numero limitado de asistentes, por lo tanto a traves de este dato se hicieron reglas de negocio para el control de capacidad asi como reglas de negocio para la validacion de horarios y demas 

Los eventos reciben y devuelven `status` como texto: `borrador`, `activo`,
`cancelado`, `finalizado` o `archivado`. Por ejemplo, `"status": "activo"`.
El campo `status_id` ya no forma parte de la API. PostgreSQL valida estos
valores mediante el enum `event_status`; la migración `c8d4e6f901ab`
convierte los estados existentes y elimina la tabla de catálogo `status`.

Las sesiones reciben y devuelven `speaker_names`, por ejemplo:

```json
{
  "speaker_names": ["Ana Pérez", "Carlos López"]
}
```

Los nombres se crean automáticamente y se comparten entre usuarios. Se eliminan
espacios sobrantes y se comparan sin distinguir mayúsculas (`casefold`). La
restricción `uq_speakers_normalized_name` garantiza la unicidad de la clave.
Se conserva la primera escritura del nombre para mostrarlo. `speaker_ids` ya
no forma parte del contrato HTTP. La revisión `f6b8c0d31527` migra los nombres,
une duplicados y conserva sus asociaciones, deteniéndose si encuentra horarios
incompatibles. Dos personas con el mismo nombre se consideran el mismo ponente.

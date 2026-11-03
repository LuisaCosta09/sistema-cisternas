def filtrar_por_dono(queryset, user, campo):
    """Admin enxerga tudo; usuário comum só o que pertence a ele.

    `campo` é o caminho até o usuário dono do registro
    (por exemplo "usuario" ou "cisterna__usuario").
    """
    if user.is_staff:
        return queryset

    return queryset.filter(**{campo: user.pk})
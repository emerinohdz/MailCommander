#!/bin/sh

###################################################################
# Script para cambiar la contraseña de un usuario recibido como
# parámetro.
###################################################################


if [[ $# -eq 2 ]]; then
    if [ "x`cat /etc/passwd | awk -F: '{print $1}' | grep $1`" = "x" ]; then
        # La cuenta no existe
        exit 1
    fi

	# cambia la contraseña
	echo "$1:$2:::::" | sudo newusers

	# se cambió la contraseña con éxito
	if [[ $? -eq 0 ]]; then
#		echo "Password para la cuenta '$1' cambiado a: $PASS"
		exit 0
	fi
fi

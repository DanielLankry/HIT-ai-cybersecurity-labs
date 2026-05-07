FROM astral/uv:python3.11-trixie

# כל קוד הפרויקט יישב ב-/app (יחובר כ-volume מבחוץ)
WORKDIR /app

# מתקין תלויות לסביבת המערכת של הקונטיינר
COPY pyproject.toml ./
RUN UV_PROJECT_ENVIRONMENT=/usr/local uv sync --no-dev --no-install-project

# Chainlit ירוץ מתיקייה נפרדת כדי ש-.chainlit ו-.files
# לא ייווצרו בקוד שלך שמחובר כ-volume
WORKDIR /chainlit-runtime

CMD ["/bin/bash"]
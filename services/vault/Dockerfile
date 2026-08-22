# syntax=docker/dockerfile:1
FROM python:3.12-slim

WORKDIR /srv

# Dependencies first, in their own layer: the shared requirements change least,
# so an edit to service code does not invalidate the pip install cache.
COPY shared/requirements.txt /srv/shared/requirements.txt
COPY vault/requirements.txt /srv/vault/requirements.txt
RUN pip install --no-cache-dir -r /srv/vault/requirements.txt

# `shared` sits on the path as a top-level package; the service's own code is
# imported as `app.*` and `main`, matching how it is laid out in the repo.
COPY shared/ /srv/shared/
COPY vault/ /srv/vault/

ENV PYTHONPATH=/srv:/srv/vault
ENV PYTHONUNBUFFERED=1

WORKDIR /srv/vault
EXPOSE 8001

HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3   CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8001/health', timeout=4).status==200 else 1)"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]

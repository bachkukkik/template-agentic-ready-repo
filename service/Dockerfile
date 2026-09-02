FROM python:3.12-slim

WORKDIR /app
COPY . .

# No test deps in the runtime image — the three tiers run outside it
# (tests/unit, tests/integration) or against it (tests/e2e).

EXPOSE 8000
CMD ["python", "-m", "src.main"]

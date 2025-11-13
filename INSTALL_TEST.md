# Installation Test Checklist

Test these steps to ensure others can use your project:

## ✅ Prerequisites Check
- [ ] Python 3.11+ installed
- [ ] AWS account with S3 access
- [ ] GitHub token generated

## ✅ Installation Steps
```bash
# 1. Clone
git clone https://github.com/Jira-saki/AWS-PREFECT-S3.git
cd AWS-PREFECT-S3

# 2. Virtual environment
python -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure
cp .env.example .env
# Edit .env with your credentials

# 5. Test connection
python test_connection.py

# 6. Test S3
python test_s3.py

# 7. Run pipeline
python flows/github_pipeline.py
```

## ✅ Expected Results
- [ ] test_connection.py: "✅ Authentication successful!"
- [ ] test_s3.py: "✅ Uploaded to s3://..."
- [ ] Pipeline: "✅ Pipeline completed!"
- [ ] S3 has raw/ and processed/ folders

## 🐛 Common Issues

### Issue 1: ModuleNotFoundError
**Solution:** Make sure venv is activated

### Issue 2: AWS credentials error
**Solution:** Check .env file format (no quotes, no spaces)

### Issue 3: pyarrow error
**Solution:** `pip install pyarrow`

---

**Test completed:** [Date]
**Tested by:** [Your name]
**Status:** ✅ All tests passed

import time
import os
import requests
from odoo import api, fields, models
from odoo import http
from odoo.exceptions import UserError, ValidationError
from odoo.http import content_disposition, request

DID_API_KEY = os.getenv("DID_API_KEY")
CHATGPT_KEY = os.getenv("CHATGPT_KEY")
DEEPSEEK_KEY = os.getenv("DEEPSEEK_KEY")
IMAGE_URL = "https://create-images-results.d-id.com/google-oauth2%7C111790638981973501987/drm_taFNiuC1RNgcnBtjhY_R1/thumbnail.jpeg"
IMAGE_URL1 = "https://create-images-results.d-id.com/google-oauth2%7C111790638981973501987/drm_2T8-WLAESOD5vQEDDTlgs/thumbnail.jpeg"
DID_URL = "https://api.d-id.com/talks"
CHATGPT_URL = "https://api.openai.com/v1/chat/completions"
DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"


class D_ID_API(models.Model):
    _name = "d.id.api"
    _description = "D-ID API"

    character = fields.Selection(
        selection=[('ch1', ('Sara')),
                   ('ch2', ('Abeer'))],
        string=("Choose Character"),
        default="ch2",
        required=True
    )
    question = fields.Text()
    lyrics = fields.Text()
    video_id = fields.Char()
    video_url = fields.Char()
    video_html = fields.Html("Video Preview", compute="_compute_video_html", sanitize=False)
    image_html = fields.Html(string="Character Image", compute="_compute_image_html", sanitize=False)

    # choose your character
    @api.depends('character')
    def _compute_image_html(self):
        for rec in self:
            if rec.character == 'ch1':
                rec.image_html = f'''
                    <div style="text-align: center; padding: 20px;">
                        <img src="{IMAGE_URL}"
                             style="max-width: 500px; max-height: 500px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);"/>
                        <br/>
                    </div>
                '''
            elif rec.character == 'ch2':
                rec.image_html = f'''
                    <div style="text-align: center; padding: 20px;">
                        <img src="{IMAGE_URL1}"
                             style="max-width: 500px; max-height: 500px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);"/>
                        <br/>
                    </div>
                '''
            else:
                rec.image_html = False

    # D-ID API Integration
    @api.depends('video_url')
    def _compute_video_html(self):
        for rec in self:
            if rec.video_url:
                rec.video_html = f'''
                        <div style="text-align: center; padding: 20px;">
                            <video width="600" controls='control' autoplay style="max-width: 100%; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                                <source src="{self.video_url}" type="video/mp4"/>
                                المتصفح لا يدعم تشغيل الفيديو.
                            </video>
                            <br/>
                        </div>
                    '''
            else:
                rec.video_html = "<p style='text-align: center; color: #999;'>لم يتم إنشاء الفيديو بعد</p>"

    def create_talking_avatar(self):
        headers = {
            "Authorization": f"Basic {DID_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "source_url": IMAGE_URL if self.character == 'ch1' else IMAGE_URL1,
            "script": {
                "type": "text",
                "input": self.lyrics,
            }
        }
        response = requests.post(DID_URL, headers=headers, json=payload)
        if response.status_code in [401, 403]:
            raise ValidationError("لا تمتلك الصلاحية")
        elif response.status_code == 402:
            raise ValidationError("لقد تجاوزت عدد المحاولات")
        elif response.status_code == 404:
            raise ValidationError("هناك خطأ برجاء المحاولة في وقت لاحق")
        elif response.status_code in [200, 201]:
            res = response.json()
            talk_id = res.get("id")
            if talk_id:
                self.video_id = talk_id
            else:
                raise UserError("D-ID API Error: %s" % res)
        self._wait_video_loading()

    def _wait_video_loading(self):
        delay = 4  # ثواني
        time.sleep(delay)
        self.fetch_video_result()

    def fetch_video_result(self):
        if not self.video_id:
            raise UserError("No video_id found. Generate video first.")
        url = f"https://api.d-id.com/talks/{self.video_id}"
        headers = {
            "Authorization": f"Basic {DID_API_KEY}"
        }
        response = requests.get(url, headers=headers)
        if response.status_code in [401, 403]:
            raise ValidationError("لا تمتلك الصلاحية")
        elif response.status_code == 402:
            raise ValidationError("لقد تجاوزت عدد المحاولات")
        elif response.status_code == 404:
            raise ValidationError("هناك خطأ برجاء المحاولة في وقت لاحق")
        elif response.status_code in [200, 201]:
            res = response.json()
            if res.get("status") != "done":
                raise UserError("Video is still processing. Try again later.")
            result_url = res.get("result_url")
            if not result_url:
                raise UserError("No video URL returned: %s" % res)
            self.video_url = result_url
        return True

    ################################################################################################
    # DEEPSEEK Integration
    def ask_deep_seek(self):
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "user",
                    "content": self.question,
                }
            ],
            "stream": False
        }
        response = requests.post(DEEPSEEK_URL, headers=headers, json=payload)
        if response.status_code in [401, 403]:
            raise ValidationError("لا تمتلك الصلاحية")
        elif response.status_code == 402:
            raise ValidationError("برجاء مراجعة سياسات الدفع إلى شركة DeepSeek")
        elif response.status_code == 404:
            raise ValidationError("هناك خطأ برجاء المحاولة في وقت لاحق")
        elif response.status_code in [200, 201]:
            res = response.json()
            answer = res.get("choices", [{}])[0].get("message", {}).get("content")
            if answer:
                self.lyrics = answer
            else:
                raise UserError("لا توجد إجاية لسؤالك هذا")
            self.create_talking_avatar()

    # ChatGPT Integration
    def ask_gpt(self):
        headers = {
            "Authorization": f"Bearer {CHATGPT_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "user",
                    "content": self.question,
                }
            ]
        }
        response = requests.post(CHATGPT_URL, headers=headers, json=payload)
        if response.status_code in [401, 403]:
            raise ValidationError("لا تمتلك الصلاحية")
        elif response.status_code == 429:
            raise ValidationError("برجاء مراجعة سياسات الدفع إلى شركة OpenAI")
        elif response.status_code == 404:
            raise ValidationError("هناك خطأ برجاء المحاولة في وقت لاحق")
        elif response.status_code in [200, 201]:
            res = response.json()
            answer = res.get("choices", [{}])[0].get("message", {}).get("content")
            if answer:
                self.lyrics = answer
            else:
                raise UserError("لا توجد إجاية لسؤالك هذا")
            self.create_talking_avatar()

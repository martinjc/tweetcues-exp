from django.contrib import admin
from django.forms import CheckboxSelectMultiple, ModelForm
from twitterexp.experiment.models import ExperimentSetting, QuestionType

class ExperimentSettingsForm(ModelForm):
    class Meta:
        model = ExperimentSetting
        widgets = {
            'possible_question_types': CheckboxSelectMultiple
        }

class QuestionTypeAdmin(admin.ModelAdmin):
    list_display = ('q_type', 'tweet_text', 'screen_name', 'name', 'avatar', 'friendship', 'follower_count', 'following_count', 'tweet_count', 'num_retweets', 'date')

class ExperimentSettingAdmin(admin.ModelAdmin):
    list_display = ('name', 'active', 'required_num_followers' , 'required_num_following', 'num_tweets_displayed', 'q_types')
    form = ExperimentSettingsForm

admin.site.register(ExperimentSetting, ExperimentSettingAdmin)
admin.site.register(QuestionType, QuestionTypeAdmin)

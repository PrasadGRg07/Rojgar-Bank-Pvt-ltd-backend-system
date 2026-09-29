"""Seed the About page with the copy that used to be hardcoded in Aboutus.jsx.

Runs once, right after the content tables are created, so the public /about page
looks exactly the same before and after switching to admin-managed content.
"""

from pathlib import Path

from django.core.files import File
from django.db import migrations

SEED_MEDIA_DIR = Path(__file__).resolve().parent.parent / "seed_media"

INTRO_PARAGRAPHS = (
    "<p><strong>ROJGAR BANK Private Limited</strong>, established in 2073 B.S., is "
    "one of Nepal&#39;s leading Human Resource, Recruitment, Training, and Workforce "
    "Outsourcing companies, headquartered in Kathmandu. With <strong>10+ years of "
    "industry experience</strong>, we have been empowering organizations with strategic "
    "workforce solutions while connecting talented professionals with rewarding career "
    "opportunities across Nepal.</p>"
    "<p>Over the years, we have earned the trust of businesses across diverse industries "
    "by delivering reliable, innovative, and results-driven HR solutions. Our "
    "comprehensive service portfolio includes recruitment and executive search, employee "
    "outsourcing, payroll administration, temporary staffing, corporate training, HR "
    "consulting, and end-to-end workforce management. Every solution is designed to help "
    "organizations enhance productivity, improve operational efficiency, and achieve "
    "sustainable business growth.</p>"
    "<p>Backed by a highly experienced HR team, a robust talent network, and modern "
    "recruitment practices, we provide customized, cost-effective, and compliant workforce "
    "solutions that create long-term value for both employers and job seekers.</p>"
)

ACHIEVEMENTS_PARAGRAPHS = (
    "<p>At <strong>ROJGAR BANK</strong>, we believe that people are the foundation of "
    "every successful organization. We are committed to helping businesses build "
    "high-performing teams while empowering individuals through professional recruitment, "
    "career development, skill enhancement, and employment opportunities.</p>"
    "<p>Driven by our core values of <strong>Integrity, Professionalism, Innovation, "
    "Excellence, and Customer Commitment</strong>, we continue to build long-term "
    "partnerships by delivering dependable, ethical, and value-driven HR solutions that "
    "exceed client expectations.</p>"
)

ACHIEVEMENTS = [
    ("10+", "Years of HR & Recruitment Excellence"),
    ("50,000+", "Qualified Candidate CV Database"),
    ("1,000+", "Successful Candidate Placements"),
    ("300+", "Corporate Clients Across Nepal"),
    ("20+", "Live Job Opportunities Published Daily"),
    ("500,000+", "Professional Network"),
]

LEADERSHIP = [
    {
        "name": "CEO",
        "role": "Chief Executive Officer",
        "image": "ceo.jpg",
        "message": (
            "<p>From my professional experience, I have realized that people are the "
            "foundation of every organization&#39;s success. At Rojgar Bank Private "
            "Limited, we are committed to bridging the gap between talent and "
            "opportunities across Nepal. Our mission has always been to build a "
            "reliable, ethical, and professional platform where job seekers can discover "
            "meaningful career opportunities and employers can find the right "
            "individuals to strengthen and grow their organizations. As we continue to "
            "expand and diversify our services.</p>"
        ),
    },
    {
        "name": "Manager",
        "role": "Recruitment Manager",
        "image": "manager.jpg",
        "message": (
            "<p>At Rojgar Bank Private Limited, we believe that every successful "
            "placement creates opportunities for both individuals and organizations to "
            "grow. Our commitment is to provide reliable, ethical, and professional "
            "recruitment services by connecting talented job seekers with the right "
            "employers across Nepal. We strive to understand the unique needs of every "
            "client and candidate, ensuring the best possible match through a "
            "transparent and efficient recruitment process. As we continue to expand our "
            "services.</p>"
        ),
    },
]

PILLARS = [
    {
        "title": "Our Mission",
        "image": "mission.jpg",
        "description": (
            "<p>To bridge the gap between employers and job seekers through professional "
            "recruitment, quality training, reliable workforce outsourcing, and strategic "
            "HR solutions while maintaining the highest standards of integrity, service "
            "excellence, innovation, and customer satisfaction.</p>"
        ),
    },
    {
        "title": "Our Vision",
        "image": "vision.jpg",
        "description": (
            "<p>To become Nepal&#39;s most trusted, innovative, and preferred human "
            "resource solutions provider by connecting people with opportunities and "
            "enabling organizations to build a future-ready workforce.</p>"
        ),
    },
    {
        "title": "Opportunities at Rojgar Bank",
        "image": "opp.jpg",
        "description": (
            "<p>At Rojgar Bank Private Limited, we believe that talented people are the "
            "key to success. We are always looking for passionate, dedicated, and skilled "
            "individuals who are eager to grow their careers while making a meaningful "
            "impact. Join our team and become part of an organization that values "
            "innovation, integrity, teamwork, and continuous professional development. "
            "Together, let&#39;s build a brighter future for Nepal&#39;s workforce.</p>"
        ),
    },
    {
        "title": "Why Choose Rojgar Bank?",
        "image": "wr.jpg",
        "description": (
            "<p>At Rojgar Bank Private Limited, we do more than just fill vacancies&mdash;we "
            "build careers and strengthen organizations. Through our personalized "
            "recruitment approach, industry expertise, and extensive network of talented "
            "professionals, we connect the right people with the right opportunities. We "
            "believe recruitment is not simply about matching candidates with jobs, but "
            "about creating meaningful careers, empowering businesses, and contributing to "
            "the long-term growth of Nepal&#39;s workforce.</p>"
        ),
    },
]

TEAM = [
    {
        "name": "Dinesh Bhatt",
        "role": "Business Development Manager",
        "image": "hr.jpg",
        "bio": (
            "<p>Business Development Manager with experience in identifying new business "
            "opportunities, building and maintaining strong client relationships, "
            "developing strategic partnerships, and driving revenue growth.</p>"
        ),
    },
    {
        "name": "Pappu Kumar Sah",
        "role": "Finance and Accounts Officer",
        "image": "fd.jpg",
        "bio": (
            "<p>Finance and Accounts Professional with experience in managing financial "
            "records, budgeting, payroll processing, taxation, bank reconciliation, "
            "invoicing, and financial reporting.</p>"
        ),
    },
    {
        "name": "Sandhya Thagunna",
        "role": "Senior Recruitment Officer",
        "image": "cfo.jpg",
        "bio": (
            "<p>Experienced Senior Recruitment Officer with expertise in end-to-end "
            "recruitment, talent acquisition, candidate sourcing, interviewing, employee "
            "onboarding, and workforce planning.</p>"
        ),
    },
]


def attach_seed_image(instance, filename):
    """Copy a bundled seed image into the active media storage."""
    source = SEED_MEDIA_DIR / filename
    if not source.exists():
        return

    with source.open("rb") as handle:
        instance.image.save(source.name, File(handle), save=False)


def seed_about_page(apps, schema_editor):
    AboutPage = apps.get_model("content", "AboutPage")
    AboutAchievement = apps.get_model("content", "AboutAchievement")
    AboutLeader = apps.get_model("content", "AboutLeader")
    AboutPillar = apps.get_model("content", "AboutPillar")
    AboutTeamMember = apps.get_model("content", "AboutTeamMember")

    # The About page is a singleton, so its row always lives at pk=1.
    AboutPage.objects.update_or_create(
        pk=1,
        defaults={
            "hero_title": "Empowering People.",
            "hero_title_highlight": "Building Organizations.",
            "hero_subtitle": (
                "Connecting talented people with meaningful opportunities while helping "
                "organizations build stronger, future-ready teams."
            ),
            "intro_paragraphs": INTRO_PARAGRAPHS,
            "show_intro": True,
            "commitment_title": "Our Commitment",
            "commitment_text": (
                "Integrity, professionalism, innovation, excellence, and customer "
                "commitment guide everything we do."
            ),
            "show_commitment": True,
            "show_achievements": True,
            "achievements_title": "Our Achievements",
            "achievements_paragraphs": ACHIEVEMENTS_PARAGRAPHS,
            "show_leadership": True,
            "leadership_title": "Leadership That Puts People First",
            "leadership_subtitle": (
                "Meet the team guiding our mission, our values, and the way we work every "
                "single day."
            ),
            "show_pillars": True,
            "pillars_title": "",
            "show_team": True,
            "team_title": "Our Team",
        },
    )

    if not AboutAchievement.objects.exists():
        AboutAchievement.objects.bulk_create(
            [
                AboutAchievement(
                    value=value,
                    label=label,
                    order=index,
                    is_active=True,
                )
                for index, (value, label) in enumerate(ACHIEVEMENTS, start=1)
            ]
        )

    if not AboutLeader.objects.exists():
        for index, entry in enumerate(LEADERSHIP, start=1):
            leader = AboutLeader(
                name=entry["name"],
                role=entry["role"],
                message=entry["message"],
                order=index,
                is_active=True,
            )
            attach_seed_image(leader, entry["image"])
            leader.save()

    if not AboutPillar.objects.exists():
        for index, entry in enumerate(PILLARS, start=1):
            pillar = AboutPillar(
                title=entry["title"],
                description=entry["description"],
                order=index,
                is_active=True,
            )
            attach_seed_image(pillar, entry["image"])
            pillar.save()

    if not AboutTeamMember.objects.exists():
        for index, entry in enumerate(TEAM, start=1):
            member = AboutTeamMember(
                name=entry["name"],
                role=entry["role"],
                bio=entry["bio"],
                order=index,
                is_active=True,
            )
            attach_seed_image(member, entry["image"])
            member.save()


def unseed_about_page(apps, schema_editor):
    AboutPage = apps.get_model("content", "AboutPage")
    AboutAchievement = apps.get_model("content", "AboutAchievement")
    AboutLeader = apps.get_model("content", "AboutLeader")
    AboutPillar = apps.get_model("content", "AboutPillar")
    AboutTeamMember = apps.get_model("content", "AboutTeamMember")

    AboutAchievement.objects.all().delete()
    AboutLeader.objects.all().delete()
    AboutPillar.objects.all().delete()
    AboutTeamMember.objects.all().delete()
    AboutPage.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_about_page, unseed_about_page),
    ]

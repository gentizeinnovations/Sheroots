# -*- coding: utf-8 -*-
"""Extra, treatment-specific content for each treatments/<slug>.html page.

DRAFT FOR CLINICAL REVIEW: written as general patient information in plain words.
Please have Dr. Chitra Karthick read and correct every entry before relying on it.
Keep it honest: no promises, no invented numbers or claims.

Each entry:
  causes   - common causes / contributing factors (list)
  sessions - what physiotherapy sessions usually involve (paragraph)
  timeline - how long recovery can take, always hedged (paragraph)
  home     - simple, safe things that help at home (list)
  urgent   - warning signs that need a doctor or emergency care first (list)
  faqs     - questions specific to this treatment: [(question, answer), ...]
"""

EXTRA = {

'neck-pain': dict(
    causes=["Long hours looking down at a phone, laptop or paperwork",
            "A desk, chair or screen set at the wrong height",
            "Sleeping with too many pillows or in an awkward position",
            "Age-related wear in the neck joints and discs (cervical spondylosis)",
            "Stress, which often shows up as tight neck and shoulder muscles"],
    sessions="Your first session looks at how your neck moves, which positions bring on the pain, and whether nerves to the arms are involved. "
             "Treatment usually combines gentle hands-on work for stiff joints and tight muscles with a few simple exercises to strengthen the deep neck "
             "and upper-back muscles. We also look at your work and phone habits, because small changes there often make the biggest difference.",
    timeline="Many people with a recent stiff or aching neck feel easier within a few weeks of regular exercise. Neck pain linked to long-standing "
             "cervical spondylosis usually needs a longer plan focused on staying flexible and strong, with flare-ups managed early. "
             "Everyone is different, and we review your progress at each visit.",
    home=["Raise your screen so the top of it is at eye level",
          "Take a short movement break every 30 to 45 minutes",
          "Use one supportive pillow that keeps your neck level",
          "Do your home exercises little and often, not all at once"],
    urgent=["Neck pain after a fall, accident or blow to the head",
            "Weakness, clumsiness or numbness in both arms or hands",
            "Problems with balance or walking",
            "Neck pain with fever, severe headache or a stiff neck you cannot bend forward"],
    faqs=[("Is cervical spondylosis curable?",
           "Cervical spondylosis describes age-related changes in the neck, which are very common. The changes themselves do not reverse, "
           "but many people have little or no pain with the right exercise, posture habits and activity."),
          ("Should I wear a neck collar?",
           "For most everyday neck pain, staying gently active is better than wearing a collar for long periods. "
           "If a doctor has advised a collar after an injury, follow that advice and we will work around it."),
          ("Can neck problems cause headaches or arm pain?",
           "Yes. Tight muscles and stiff joints in the neck can cause headaches, and an irritated nerve can send pain, tingling or "
           "numbness into the arm. Your assessment helps us find where it is coming from.")]),

'shoulder-pain': dict(
    causes=["Repeated reaching, lifting or overhead work",
            "Irritated or weak rotator cuff tendons",
            "Frozen shoulder (adhesive capsulitis), which is more common in people with diabetes and in midlife",
            "Falls or injuries such as a strain or dislocation",
            "Rounded posture that changes how the shoulder blade moves"],
    sessions="We first check how your shoulder and shoulder blade move, which movements hurt, and whether the neck is involved. "
             "Treatment depends on the cause: for tendon problems the focus is gradual strengthening, while for frozen shoulder we use gentle "
             "mobilisation and stretches within your comfort. You will leave each session knowing exactly what to practise at home.",
    timeline="Shoulder strains and tendon problems often improve over several weeks to a few months of steady exercise. "
             "Frozen shoulder is different: it tends to move through painful, stiff and recovery stages and can take many months to settle. "
             "Physiotherapy aims to keep you as comfortable and mobile as possible along the way.",
    home=["Keep the arm moving gently within a comfortable range",
          "Avoid sleeping on the painful side; hug a pillow for support",
          "Use a warm pack before your exercises if it helps stiffness",
          "Break heavy or overhead tasks into shorter spells"],
    urgent=["Shoulder or arm pain with chest pain, breathlessness or sweating (call emergency services)",
            "Being unable to lift the arm at all after a fall or injury",
            "A shoulder that looks out of place",
            "A hot, red, swollen joint or fever"],
    faqs=[("How do I know if I have a frozen shoulder?",
           "Frozen shoulder usually causes pain and a steady loss of movement in every direction, especially turning the arm outwards. "
           "A physiotherapy assessment, and sometimes your doctor, can confirm it."),
          ("Should I rest my shoulder completely?",
           "Complete rest usually makes a stiff shoulder stiffer. We will show you which movements are safe and how much to do."),
          ("Can physiotherapy help after shoulder surgery?",
           "Yes. Rehabilitation after surgery follows your surgeon's protocol, and we guide you step by step through each stage.")]),

'tennis-elbow': dict(
    causes=["Repeated gripping, twisting or lifting with the wrist bent back",
            "Long hours of typing or using a mouse",
            "Household tasks such as wringing clothes, chopping or carrying bags",
            "Racquet sports or gym work with poor technique or a sudden increase in load",
            "Manual jobs using tools"],
    sessions="We confirm where the pain comes from, test your grip and look at the tasks that bring it on. "
             "The core of treatment is a carefully progressed strengthening programme for the forearm tendons, alongside soft-tissue work "
             "and practical changes to how you grip, lift and set up your workstation.",
    timeline="Tennis elbow often settles slowly. Many people improve over a few months when they manage load and keep up their exercises, "
             "though some cases take longer. Steady, consistent work tends to matter more than any single treatment.",
    home=["Lift with your palm facing up where you can",
          "Use a thicker grip on tools, pens and handles",
          "Spread repetitive tasks through the day",
          "Keep doing your strengthening exercises even when pain eases"],
    urgent=["Severe pain, swelling or deformity after a fall",
            "Numbness or weakness in the hand that is getting worse",
            "A hot, red, swollen elbow or fever"],
    faqs=[("Can I get tennis elbow if I don't play tennis?",
           "Yes. Most people with tennis elbow do not play tennis. Any task that repeatedly loads the forearm tendons can cause it."),
          ("Will a tennis elbow strap help?",
           "Some people find a forearm strap reduces pain during activity. It works best alongside strengthening exercises, not instead of them."),
          ("Should I stop using my arm?",
           "Usually not completely. We help you find the right amount of activity so the tendon is loaded enough to recover without flaring up.")]),

'back-pain-sciatica': dict(
    causes=["Sitting for long periods, especially with little movement",
            "Lifting or bending awkwardly",
            "Weak or deconditioned back, hip and core muscles",
            "Disc changes that irritate a nerve and cause sciatica",
            "Pregnancy, weight changes or stress"],
    sessions="Your assessment covers how your back moves, nerve tests for the legs, and the activities that ease or worsen your pain. "
             "Treatment combines hands-on techniques to reduce pain and stiffness with exercises to move and strengthen the back, hips and core. "
             "We also explain what is happening in plain words, because understanding your pain is an important part of recovery.",
    timeline="Many episodes of low back pain improve within a few weeks, and sciatica often settles over a few weeks to a few months. "
             "Staying gently active usually helps more than bed rest. If pain keeps coming back, we focus on building strength and confidence "
             "to reduce future flare-ups.",
    home=["Keep moving: short, frequent walks are often helpful",
          "Change position regularly when sitting",
          "Bend your knees and keep loads close when lifting",
          "Use heat if it eases muscle spasm"],
    urgent=["Numbness around the groin, inner thighs or back passage",
            "New difficulty passing urine, or loss of bladder or bowel control",
            "Weakness in both legs or a foot that drags",
            "Back pain with fever, unexplained weight loss, or after a significant fall"],
    faqs=[("Should I rest in bed with back pain?",
           "For most back pain, staying gently active is better than bed rest. We will show you safe ways to move and stay active."),
          ("Do I need an MRI scan?",
           "Most back pain does not need a scan. Your doctor may advise one if there are warning signs or if symptoms do not improve as expected."),
          ("What is the difference between back pain and sciatica?",
           "Back pain is felt mainly in the back. Sciatica is pain, tingling or numbness that travels down the leg, usually from an irritated nerve in the lower back.")]),

'knee-pain': dict(
    causes=["Age-related wear in the joint (osteoarthritis)",
            "Weak thigh and hip muscles that leave the knee less supported",
            "Twisting injuries to ligaments or the meniscus",
            "Pain around the kneecap from overuse, stairs or squatting",
            "Extra body weight, which increases load on the knee"],
    sessions="We assess how you walk, climb stairs and squat, and test the strength of the muscles around the hip and knee. "
             "Treatment focuses on strengthening exercises that support the joint, movement work for stiffness, and practical advice on walking, "
             "stairs and sitting on the floor, so you can keep doing the things that matter to you.",
    timeline="Knee pain from overuse often improves over several weeks of strengthening. For osteoarthritis, exercise is a long-term habit rather "
             "than a short course, and many people find their pain and walking improve as their muscles get stronger.",
    home=["Keep active with walking or cycling at a comfortable level",
          "Do your strengthening exercises on most days",
          "Use a handrail on stairs while the knee is painful",
          "Avoid long periods kneeling or squatting during flare-ups"],
    urgent=["A knee that is hot, red and swollen, especially with fever",
            "Being unable to put weight on the leg after an injury",
            "A knee that locks and cannot be straightened",
            "Calf pain and swelling, which can be a sign of a blood clot"],
    faqs=[("Will exercise make my knee arthritis worse?",
           "The right exercise is one of the most helpful treatments for knee osteoarthritis. We start at a level that suits you and build up gradually."),
          ("Can physiotherapy help me avoid knee surgery?",
           "For many people, exercise and activity changes reduce pain enough that surgery is not needed. If surgery is the right choice, "
           "physiotherapy before and after helps recovery."),
          ("Can I sit cross-legged or on the floor?",
           "It depends on your knee. We will look at what is comfortable for you and work on the movement if it matters in your daily life.")]),

'ankle-sprain': dict(
    causes=["Rolling the ankle on uneven ground or a step",
            "An awkward landing during sport or exercise",
            "Footwear with poor support",
            "A previous sprain that left the ankle weaker or less stable",
            "Reduced balance and ankle strength"],
    sessions="We check how badly the ligaments are affected and rule out signs that need an X-ray. "
             "Early sessions focus on settling swelling and getting you walking normally. As it heals, we add strength, balance and agility "
             "work so the ankle is ready for daily life or sport.",
    timeline="Mild sprains often feel much better within a few weeks, while more severe sprains can take a few months to fully recover. "
             "Balance and strength training lowers the chance of spraining it again.",
    home=["Protect the ankle and rest it for the first day or two",
          "Raise the leg when sitting to reduce swelling",
          "Start gentle ankle movements as pain allows",
          "Practise standing on one leg once walking is comfortable"],
    urgent=["Being unable to take four steps after the injury",
            "Pain directly on the ankle bones or the outer edge of the foot",
            "The ankle looks deformed or out of place",
            "Numbness or coldness in the foot"],
    faqs=[("Do I need an X-ray for a sprained ankle?",
           "Not always. If you cannot walk, or there is pain on specific bones, an X-ray may be needed to check for a fracture. We will tell you if you should see a doctor."),
          ("Should I use ice or heat?",
           "In the first few days, a cold pack can help with pain. Later, gentle movement matters more than either."),
          ("Why does my ankle keep giving way?",
           "After a sprain the ligaments and balance system can stay weaker. Targeted balance and strength exercises usually help.")]),

'posture-correction': dict(
    causes=["Many hours at a desk, laptop or phone",
            "Carrying children on one hip or heavy bags on one side",
            "Weak upper-back, core and hip muscles",
            "Tight chest and hip muscles from sitting",
            "Tiredness and stress, which change how we hold ourselves"],
    sessions="We look at how you sit, stand, lift and work, and check which muscles are tight or weak. "
             "Rather than chasing a 'perfect' posture, we help you move more and vary your positions, with a short routine of strengthening "
             "and stretching exercises and practical changes to your workstation and daily habits.",
    timeline="Many people notice less end-of-day aching within a few weeks of changing habits and exercising. Lasting change comes from keeping "
             "the routine going, so we keep it short and realistic.",
    home=["Set up your screen at eye level and your chair to support your back",
          "Change position often; the best posture is your next one",
          "Swap sides when carrying children or bags",
          "Do a few shoulder-blade squeezes and chest stretches each day"],
    urgent=["Pain with numbness, tingling or weakness in the arms or legs",
            "A visible change in the shape of the spine that is getting worse",
            "Back pain with fever or unexplained weight loss"],
    faqs=[("Is there one correct posture?",
           "No. Bodies are built differently, and staying still in any position for too long can cause aches. Moving and changing position is what matters most."),
          ("Do posture correctors or braces work?",
           "They may remind you to sit up for a while, but they do not build strength. Exercise and habit changes give longer-lasting results."),
          ("Can posture be improved at any age?",
           "Yes. Strength and flexibility can improve at any age with regular, suitable exercise.")]),

'sports-injuries': dict(
    causes=["A sudden increase in training load or intensity",
            "Poor warm-up or recovery",
            "Muscle imbalances or reduced flexibility",
            "Technique problems or unsuitable footwear and equipment",
            "Returning too early after a previous injury"],
    sessions="We assess the injured area and look at how you move during the activities you do. "
             "Your plan moves in stages: settling pain, restoring movement, rebuilding strength and power, and finally sport-specific work, "
             "so you return with confidence. We also look at training habits that may have contributed.",
    timeline="Recovery time depends on the type and severity of the injury, from a couple of weeks for a minor strain to several months for more "
             "serious problems. We use clear milestones rather than guesswork to decide when you are ready to return.",
    home=["Stay active with exercise that does not aggravate the injury",
          "Follow the stages of your plan rather than rushing back",
          "Sleep well and eat well to support healing",
          "Warm up properly before training"],
    urgent=["A 'pop' with immediate swelling and being unable to bear weight",
            "A joint that looks deformed",
            "Any head injury with confusion, vomiting or loss of consciousness",
            "Numbness, coldness or colour change in a limb"],
    faqs=[("When can I go back to my sport?",
           "When you have met clear goals for strength, movement and confidence, not just when the pain stops. We test this together."),
          ("Can I keep training while injured?",
           "Often you can keep training in a modified way. We help you find what is safe so you stay fit while recovering."),
          ("Do you see non-professional athletes?",
           "Yes. Whether you walk, run, play cricket or go to the gym, the same principles apply.")]),

'joint-pain': dict(
    causes=["Osteoarthritis (age-related wear in the joints)",
            "Inflammatory conditions such as rheumatoid arthritis, managed with your doctor",
            "Previous injuries",
            "Reduced activity and muscle weakness",
            "Extra body weight placing more load on the joints"],
    sessions="We assess which joints are affected, how they move and how they affect your daily life. "
             "Treatment combines gentle mobility work, strengthening to support the joints, and advice on pacing so you can stay active without "
             "flare-ups. If an inflammatory condition is suspected, we will advise you to see your doctor.",
    timeline="Joint pain linked to arthritis is usually managed over the long term. Many people find that regular, suitable exercise reduces pain "
             "and stiffness over a few months and helps them stay independent.",
    home=["Move little and often, especially after resting",
          "Use warmth to ease morning stiffness",
          "Balance activity with rest during flare-ups",
          "Choose joint-friendly exercise such as walking or cycling"],
    urgent=["A single joint that becomes suddenly hot, red and swollen",
            "Joint pain with fever or feeling generally unwell",
            "Joint pain after a fall with inability to use the limb"],
    faqs=[("Is it safe to exercise with arthritis?",
           "Yes. Suitable exercise is recommended for most types of arthritis. We tailor it to your joints and build it up slowly."),
          ("Why are my joints stiff in the morning?",
           "Joints often stiffen after rest. Gentle movement usually helps. Long-lasting morning stiffness can be a sign of an inflammatory condition, which your doctor should check."),
          ("Can physiotherapy replace my medicines?",
           "No. Physiotherapy works alongside the treatment your doctor prescribes. Always speak to your doctor before changing medicines.")]),

'wrist-carpal-tunnel': dict(
    causes=["Repeated wrist bending during typing, sewing, cutting or tool use",
            "Pregnancy, when fluid changes can squeeze the nerve",
            "Hormonal changes, thyroid problems or diabetes",
            "Wrist injuries or arthritis",
            "Holding a phone or steering wheel for long periods"],
    sessions="We check where your symptoms are, test grip and sensation, and look at the tasks that bring them on. "
             "Treatment can include nerve-gliding and strengthening exercises, advice on hand use and workstation set-up, and, where suitable, "
             "guidance on wearing a night splint to keep the wrist straight while you sleep.",
    timeline="Mild carpal tunnel symptoms often improve over several weeks with splinting and activity changes. Carpal tunnel during pregnancy "
             "often eases after birth. If symptoms are severe or getting worse, we will advise you to see your doctor.",
    home=["Keep your wrist straight when typing and sleeping",
          "Take regular breaks from repetitive hand tasks",
          "Shake out or gently move your hands when they tingle",
          "Avoid gripping too hard on tools and phones"],
    urgent=["Constant numbness or weakness that is getting worse",
            "Wasting of the muscles at the base of the thumb",
            "Severe pain, swelling or deformity after a fall"],
    faqs=[("Why is the tingling worse at night?",
           "Many people bend their wrists while sleeping, which increases pressure on the nerve. A night splint can help keep the wrist straight."),
          ("Can pregnancy cause carpal tunnel?",
           "Yes. Fluid changes in pregnancy can squeeze the nerve. It often settles after birth, and physiotherapy can ease symptoms meanwhile."),
          ("Will I need surgery?",
           "Many people improve without surgery. If symptoms are severe or do not improve, your doctor may discuss other options.")]),

'cardiac-rehabilitation': dict(
    causes=["Recovery after a heart attack",
            "After bypass surgery, valve surgery or a stent",
            "Living with heart failure or angina, as advised by your cardiologist",
            "Reduced fitness and confidence after a heart event",
            "Wanting to build healthy, sustainable activity habits"],
    sessions="Cardiac rehabilitation is planned with your doctor's advice in mind. We check how you feel during activity and progress exercise "
             "gradually, mixing walking or cycling with light strengthening. Sessions also cover pacing, recognising warning signs, and building "
             "confidence to return to daily life.",
    timeline="Cardiac rehabilitation usually runs over several weeks, with the aim of building habits you continue for life. "
             "Progress depends on your condition and your doctor's guidance.",
    home=["Follow your cardiologist's advice and take medicines as prescribed",
          "Walk regularly at a pace where you can still talk",
          "Build up activity gradually rather than doing a lot on one day",
          "Stop and rest if you feel unwell during exercise"],
    urgent=["Chest pain, pressure or tightness that does not settle with rest (call emergency services)",
            "Sudden breathlessness, fainting or a very fast or irregular heartbeat",
            "Sudden weakness of the face, arm or leg, or difficulty speaking"],
    faqs=[("Do I need my doctor's permission?",
           "Yes. We work alongside your cardiologist and ask about any limits they have given you before starting."),
          ("Is exercise safe after a heart attack?",
           "Supervised, gradual exercise is a standard part of recovery for many people after a heart event. We start gently and progress carefully."),
          ("What if I feel unwell during a session?",
           "We monitor how you feel throughout, stop if needed, and will direct you to urgent care if symptoms suggest it.")]),

'weight-loss': dict(
    causes=["Joint or back pain that makes exercise difficult",
            "Weight gained during pregnancy or after an injury",
            "Busy routines with little time for activity",
            "Hormonal conditions such as PCOS or thyroid problems, managed with your doctor",
            "Not knowing where to start or how to stay consistent"],
    sessions="We look at your health history, any pain or joint problems, and your current activity level. "
             "Together we build a safe, progressive plan mixing strength work and cardiovascular exercise that protects your joints, "
             "with regular check-ins to adjust the plan and keep you on track. We work alongside your doctor or dietitian where needed.",
    timeline="Healthy weight change is gradual. Many people notice better energy, strength and fitness within a few weeks of regular exercise, "
             "even before the scales change. Food and sleep play a big part too.",
    home=["Aim for regular movement on most days, even short walks",
          "Add two or three strength sessions a week",
          "Track your progress by how you feel and what you can do, not only weight",
          "Pair exercise with balanced meals and good sleep"],
    urgent=["Chest pain, fainting or severe breathlessness during exercise",
            "Rapid, unexplained weight loss or gain",
            "New swelling of the legs"],
    faqs=[("Can physiotherapy alone make me lose weight?",
           "Exercise is one part. Weight change also depends on diet, sleep and health conditions. We focus on safe, sustainable activity and can work alongside a dietitian."),
          ("I have knee pain. Can I still exercise?",
           "Yes. We choose exercises that strengthen without overloading painful joints, and progress them gradually."),
          ("How often should I exercise?",
           "Most adults benefit from regular movement on most days. We help you build up to a routine that fits your life.")]),

'pelvic-floor': dict(
    causes=["Pregnancy and vaginal birth",
            "Hormonal changes around menopause",
            "Long-term constipation and straining",
            "A chronic cough or heavy lifting",
            "Pelvic floor muscles that are too tight, which can cause pain"],
    sessions="Your first session starts with a private conversation about your symptoms. We explain everything before any assessment, "
             "and nothing happens without your consent. Treatment usually includes learning to contract and relax the pelvic floor correctly, "
             "a personal exercise programme, breathing techniques, and advice on bladder and bowel habits.",
    timeline="Pelvic floor muscles, like other muscles, take time to strengthen. Many people notice changes after a few months of regular exercise. "
             "If the muscles are tight rather than weak, the focus is on relaxation, and progress varies.",
    home=["Practise your pelvic floor exercises daily as shown",
          "Avoid straining on the toilet; keep stools soft with fluids and fibre",
          "Breathe out as you lift heavy things",
          "Do not 'go just in case' too often, which can train the bladder to hold less"],
    urgent=["Blood in your urine",
            "Sudden inability to pass urine",
            "Heavy or unusual vaginal bleeding, or bleeding after menopause",
            "Pelvic pain with fever"],
    faqs=[("Is pelvic floor physiotherapy only for women who have given birth?",
           "No. Pelvic floor problems can affect women at any age, including those who have never been pregnant, and men too."),
          ("Is an internal examination needed?",
           "Not always. We explain the options, and you choose what you are comfortable with. Many people improve with an external assessment and exercises alone."),
          ("How do I know I'm doing the exercises correctly?",
           "Many people do them incorrectly without realising. Part of the assessment is checking your technique and giving you clear feedback.")]),

'postnatal-care': dict(
    causes=["Stretching of the core and pelvic floor during pregnancy",
            "Vaginal birth, tears or an episiotomy",
            "Caesarean section recovery",
            "Feeding, lifting and carrying positions that strain the back and neck",
            "Lack of sleep and time for yourself"],
    sessions="We check your core, pelvic floor and any scar, and talk about your birth and how you are feeling now. "
             "Treatment includes gentle core and pelvic floor rehabilitation, safe positions for feeding and lifting, scar care where relevant, "
             "and a step-by-step return to exercise. You are welcome to bring your baby.",
    timeline="Recovery after birth takes months, not weeks, and every birth is different. Gentle exercise can usually start soon after birth, "
             "with higher-impact activity such as running introduced gradually once your body is ready.",
    home=["Start gentle pelvic floor and breathing exercises when comfortable",
          "Support your back with pillows while feeding",
          "Bend your knees and keep your baby close when lifting",
          "Rest when you can, and ask for help"],
    urgent=["Heavy bleeding, large clots or foul-smelling discharge",
            "Fever, or a red, hot or weeping wound",
            "Calf pain or swelling, chest pain or sudden breathlessness",
            "Feeling very low, anxious or unable to cope"],
    faqs=[("When can I start postnatal physiotherapy?",
           "Gentle advice and exercises can begin early. A full check is often helpful around six weeks after birth, or once your doctor is happy with your recovery."),
          ("Is it safe after a caesarean?",
           "Yes, with a plan adjusted to your scar and recovery. We follow any advice from your doctor."),
          ("When can I return to running or the gym?",
           "We check your strength and pelvic floor first, then guide a gradual return. Many women need a few months before high-impact exercise.")]),

'pcos-pcod': dict(
    causes=["PCOS/PCOD is a hormonal condition diagnosed by your doctor",
            "Insulin resistance, which exercise may help improve",
            "Low activity levels or irregular routines",
            "Weight changes that can be hard to manage",
            "Tiredness and low motivation that make exercise difficult"],
    sessions="We talk about your diagnosis, your routine and what has or has not worked before. "
             "We then build a realistic programme mixing strength training and cardiovascular exercise, with pacing advice so it fits your life. "
             "Physiotherapy works alongside your doctor's treatment; it does not replace it.",
    timeline="Regular exercise over several months is generally recommended as part of PCOS/PCOD management. Many women notice better energy "
             "and fitness first. Other changes depend on your condition and your doctor's treatment.",
    home=["Aim for some movement every day",
          "Include strength training two or three times a week",
          "Keep a regular sleep routine",
          "Follow your doctor's and dietitian's advice on food and medicines"],
    urgent=["Very heavy periods, or bleeding between periods",
            "Severe pelvic pain",
            "Missed periods with a possible pregnancy",
            "Feeling very low or anxious"],
    faqs=[("Can physiotherapy cure PCOS/PCOD?",
           "No. PCOS/PCOD is managed by your doctor. Exercise is commonly recommended as part of that management, and we help you do it safely and consistently."),
          ("What type of exercise is best for PCOS/PCOD?",
           "A mix of strength training and cardiovascular exercise is commonly recommended. The best plan is one you can keep doing."),
          ("Do I need a diagnosis before starting?",
           "Yes. PCOS/PCOD should be diagnosed by a doctor. We are happy to work alongside them.")]),

'dry-needling': dict(
    causes=["Persistent muscle tightness or 'knots' (trigger points)",
            "Neck, shoulder and upper-back muscle pain",
            "Low back and buttock muscle tension",
            "Overuse in sport or physical work",
            "Muscle pain that has not settled with exercise alone"],
    sessions="Dry needling is only used after an assessment shows it may suit you, and always with your consent. "
             "We explain what it involves, use single-use sterile needles, and combine it with movement and exercise as part of a wider plan. "
             "If you prefer not to have needling, other techniques can be used instead.",
    timeline="Some people feel easier movement soon after a session, while others need a few sessions to notice a difference. "
             "Mild soreness for a day or two afterwards is common. Dry needling works best as one part of an active plan.",
    home=["Keep moving gently after a session",
          "Use warmth if you feel muscle soreness",
          "Drink water and continue your home exercises",
          "Tell us about any unusual reactions at your next visit"],
    urgent=["Sudden breathlessness or chest pain after needling near the chest wall (seek emergency care)",
            "Signs of infection at a needle site: spreading redness, heat or fever",
            "Fainting or feeling very unwell"],
    faqs=[("Is dry needling the same as acupuncture?",
           "They use similar needles but are based on different approaches. Dry needling targets tight spots in muscles as part of physiotherapy treatment."),
          ("Does dry needling hurt?",
           "Most people feel a small prick and sometimes a brief twitch or ache in the muscle. We check your comfort throughout."),
          ("Who should not have dry needling?",
           "It may not be suitable in some situations, such as early pregnancy, bleeding disorders, a fear of needles or certain medical conditions. We check this before starting.")]),

'pregnancy-care': dict(
    causes=["Hormonal changes that make ligaments more flexible",
            "A growing bump that changes posture and balance",
            "Extra load on the back, pelvis and hips",
            "Reduced activity due to tiredness or worry",
            "Previous back or pelvic pain"],
    sessions="We ask about your pregnancy, your doctor's advice and what you would like to feel more confident about. "
             "Sessions can include safe exercise, techniques to ease back and pelvic pain, pelvic floor and breathing work, and preparation for birth "
             "and recovery. We always work within your doctor's guidance.",
    timeline="Support can start at any stage of pregnancy. Many women find pain becomes easier to manage within a few sessions, and keeping active "
             "through pregnancy helps with birth preparation and recovery.",
    home=["Stay active with walking, swimming or approved exercise",
          "Sleep on your side with a pillow between your knees",
          "Keep your knees together when getting in and out of bed or a car",
          "Practise your pelvic floor and breathing exercises"],
    urgent=["Vaginal bleeding or fluid leaking",
            "Severe headache, vision changes or sudden swelling of the face or hands",
            "Reduced baby movements",
            "Regular tightenings or pain before 37 weeks"],
    faqs=[("Is it safe to exercise during pregnancy?",
           "For most healthy pregnancies, regular moderate exercise is recommended. Always check with your doctor, and we will adapt exercises to you."),
          ("Can physiotherapy help pelvic girdle pain?",
           "Yes. Advice, exercises and practical techniques often make pelvic girdle pain much easier to manage."),
          ("When should I start pregnancy physiotherapy?",
           "Any time. Some women come early for exercise advice, others when pain starts or as birth approaches.")]),

'diastasis-recti': dict(
    causes=["Stretching of the tummy muscles during pregnancy",
            "More than one pregnancy, or a large baby or twins",
            "Straining, heavy lifting or a chronic cough",
            "Weak deep core muscles",
            "Returning to intense abdominal exercise too soon"],
    sessions="We measure the gap and check how well the tissue between the muscles tenses, which matters as much as the width. "
             "Treatment focuses on deep core and breathing exercises, safe lifting and daily movement habits, and a graded return to "
             "the exercise you enjoy.",
    timeline="Some separation is normal after pregnancy and often improves on its own in the first months. With exercise, many women see gradual "
             "improvement in strength and function over a few months. A small gap may remain without causing problems.",
    home=["Roll onto your side to get out of bed",
          "Breathe out and gently draw your tummy in when lifting",
          "Avoid straining on the toilet",
          "Pause full sit-ups and crunches until you have been assessed"],
    urgent=["A painful bulge that cannot be pushed back (possible hernia)",
            "Severe tummy pain, vomiting or fever",
            "Bleeding or discharge from a scar"],
    faqs=[("How do I know if I have diastasis recti?",
           "You may notice a bulge or 'doming' along the middle of your tummy when you sit up. An assessment can measure the gap and check the tissue."),
          ("Can diastasis recti improve years after pregnancy?",
           "Yes. Core strength and function can improve with the right exercise at any time, even years later."),
          ("Should I avoid all abdominal exercise?",
           "No. The right core exercises are an important part of recovery. We show you which ones to do now and which to build up to.")]),

'urinary-incontinence': dict(
    causes=["Weak pelvic floor muscles after pregnancy or birth",
            "Hormonal changes around menopause",
            "An overactive bladder that causes sudden urges",
            "Constipation, a chronic cough or heavy lifting",
            "Drinking a lot of tea, coffee or fizzy drinks"],
    sessions="We start with a private, relaxed conversation about your bladder habits and symptoms, and you may be asked to keep a simple bladder diary. "
             "Treatment includes pelvic floor training, bladder retraining for urgency, and practical strategies for exercise and daily life. "
             "Everything is explained first and done only with your consent.",
    timeline="Pelvic floor training usually needs a few months of regular practice to show its full effect. Many people notice fewer leaks earlier. "
             "Bladder retraining for urgency also takes several weeks.",
    home=["Do your pelvic floor exercises every day",
          "Drink enough water spread through the day",
          "Cut down on tea, coffee and fizzy drinks",
          "Try to stretch the time between toilet visits gradually, as advised"],
    urgent=["Blood in your urine",
            "Pain or burning when passing urine, with fever",
            "Sudden loss of bladder control with back pain or numbness",
            "Being unable to pass urine"],
    faqs=[("Is leaking urine a normal part of ageing or having children?",
           "It is common, but it is not something you simply have to accept. Many people improve with the right exercises and habits."),
          ("What is the difference between stress and urge incontinence?",
           "Stress incontinence is leaking with coughing, sneezing or exercise. Urge incontinence is a sudden strong need to go. Some people have both."),
          ("Will I need surgery?",
           "Pelvic floor training is usually recommended first. If it does not help enough, your doctor may discuss other options.")]),
}

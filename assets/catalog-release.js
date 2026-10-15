import { storedCatalogData } from './catalog-data.js';
export const RELEASE_ID = '946b05b6d128cd88ac8ba09431cb645ae80a453d';
// Newly published main-branch links; never writes to Firebase.
// Existing server titles, visibility, custom items and ordering are preserved.
export const RELEASE_ADDITIONS = [
  {
    "grade": "Grade 5",
    "unit": "Bổ trợ ngữ pháp",
    "lesson": {
      "title": "Unit 13 Future – Will: Affirmatives & Negatives",
      "href": "grade-5/Bo_Tro_Ngu_Phap/unit_13_future_will.html"
    },
    "before": "grade-5/Bo_Tro_Ngu_Phap/unit_3_MANY  MUCH  A LOT OF.html"
  },
  {
    "grade": "Grade 5",
    "unit": "Bổ trợ ngữ pháp",
    "lesson": {
      "title": "Unit 14 Future – Will: Yes/No & What Questions",
      "href": "grade-5/Bo_Tro_Ngu_Phap/unit_14_future_will_yes_no_questions_what_questions_worksheet.html"
    },
    "before": "grade-5/Bo_Tro_Ngu_Phap/unit_3_MANY  MUCH  A LOT OF.html"
  },
  {
    "grade": "Grade 5",
    "unit": "Bổ trợ ngữ pháp",
    "lesson": {
      "title": "Unit 15 Future – Be Going To",
      "href": "grade-5/Bo_Tro_Ngu_Phap/unit_15_future_be_going_to.html"
    },
    "before": "grade-5/Bo_Tro_Ngu_Phap/unit_3_MANY  MUCH  A LOT OF.html"
  },
  {
    "grade": "Grade 5",
    "unit": "Bổ trợ ngữ pháp",
    "lesson": {
      "title": "Unit 16 Future – Be Going To: Questions",
      "href": "grade-5/Bo_Tro_Ngu_Phap/unit_16_future_be_going_to.html"
    },
    "before": "grade-5/Bo_Tro_Ngu_Phap/unit_3_MANY  MUCH  A LOT OF.html"
  },
  {
    "grade": "Grade 5",
    "unit": "Bổ trợ ngữ pháp",
    "lesson": {
      "title": "Unit 17 Adverbs of Manner",
      "href": "grade-5/Bo_Tro_Ngu_Phap/unit_17_adverbs_of_manner.html"
    },
    "before": "grade-5/Bo_Tro_Ngu_Phap/unit_3_MANY  MUCH  A LOT OF.html"
  },
  {
    "grade": "Grade 5",
    "unit": "Bổ trợ ngữ pháp",
    "lesson": {
      "title": "Unit 18 Adverbs of Frequency I",
      "href": "grade-5/Bo_Tro_Ngu_Phap/UNIT_18_ ADVERBS OF FREQUENCY I.html"
    },
    "before": "grade-5/Bo_Tro_Ngu_Phap/unit_3_MANY  MUCH  A LOT OF.html"
  }
];

export const IELTS_RELEASE_ID = 'c16c5eb75c40c0b52a58622a499b446ae1fdd356';
export const RELEASE_IDS = [RELEASE_ID, IELTS_RELEASE_ID];
const previousAdditions = RELEASE_ADDITIONS.length;
RELEASE_ADDITIONS.push({
  grade: 'Apps for IELTS', unit: 'IELTS Writing',
  lesson: {title: 'Luyện viết IELTS', href: 'Apps for IELTS/Luyện viết IELTS.html'}
});

export function addReleaseLessons(serverData, applied = []) {
  const data = structuredClone(serverData);
  const existing = new Set(data.flatMap(g => g.units.flatMap(u => u.lessons.map(l => l.href))));
  let added = 0;
  for (const [index, patch] of RELEASE_ADDITIONS.entries()) {
    if (applied.includes(index < previousAdditions ? RELEASE_ID : IELTS_RELEASE_ID)) continue;
    if (existing.has(patch.lesson.href)) continue; // Includes already-hidden lessons.
    const prefix = patch.lesson.href.slice(0, patch.lesson.href.lastIndexOf('/') + 1);
    let grade = data.find(g => g.grade === patch.grade) || data.find(g => g.units.some(u => u.lessons.some(l => l.href.startsWith(prefix))));
    if (!grade) { grade = {grade: patch.grade, units: []}; data.push(grade); }
    let unit = grade.units.find(u => u.name === patch.unit) || grade.units.find(u => u.lessons.some(l => l.href.startsWith(prefix)));
    if (!unit) { unit = {name: patch.unit, lessons: []}; grade.units.push(unit); }
    const before = unit.lessons.findIndex(l => l.href === patch.before);
    unit.lessons.splice(before < 0 ? unit.lessons.length : before, 0, structuredClone(patch.lesson));
    existing.add(patch.lesson.href); added++;
  }
  return {data, added};
}

export function releaseCatalogView(fields, serverData) {
  return addReleaseLessons(serverData, storedCatalogData(fields).releaseApplied).data;
}

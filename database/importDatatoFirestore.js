const csv = require('csv-parse');
const fs = require('fs');
const { Firestore } = require('@google-cloud/firestore');
const { Logging } = require('@google-cloud/logging');
const logName = 'pet-theory-logs-importTestData';

// Creates a Logging client
const logging = new Logging();
const log = logging.log(logName);

const resource = {
  type: 'global',
};

function writeToDatabase(records) {
  records.forEach((record, i) => {
    console.log(
      `place_id: ${record.place_id} name: ${record.name} rating: ${record.rating} reviews_count: ${record.reviews_count} long: ${record.long} lat: ${record.lat} address: ${record.address} caption_idn: ${record.caption_idn} caption_eng: ${record.caption_eng}`
    );
  });
  return;
}

async function importCsv(csvFilename) {
  const parser = csv.parse(
    { columns: true, delimiter: ',' },
    async function (err, records) {
      if (err) {
        console.error('Error parsing CSV:', err);
        return;
      }
      try {
        console.log(`Call write to Firestore`);
        await writeToFirestore(records);
        // await writeToDatabase(records);
        console.log(`Wrote ${records.length} records`);
        // A text log entry
        success_message = `Success: importTestData - Wrote ${records.length} records`;
        const entry = log.entry(
          { resource: resource },
          { message: `${success_message}` }
        );
        log.write([entry]);
      } catch (e) {
        console.error(e);
        process.exit(1);
      }
    }
  );

  await fs.createReadStream(csvFilename).pipe(parser);
}

if (process.argv.length < 3) {
  console.error('Please include a path to a csv file');
  process.exit(1);
}

async function writeToFirestore(records) {
  const db = new Firestore({
    // projectId: projectId
  });
  const batch = db.batch();

  records.forEach((record) => {
    console.log(`Write: ${record}`);
    const docRef = db.collection('location').doc(record.place_id);
    batch.set(docRef, record, { merge: true });
  });

  batch
    .commit()
    .then(() => {
      console.log('Batch executed');
    })
    .catch((err) => {
      console.log(`Batch error: ${err}`);
    });
  return;
}

importCsv(process.argv[2]).catch((e) => console.error(e));

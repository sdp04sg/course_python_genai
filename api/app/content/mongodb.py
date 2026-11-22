from app.content._build import lesson, question, section

CONTENT = {
    "mongo-intro": lesson(
        "MongoDB stores data as flexible, JSON-like documents grouped into collections. Run it in Docker, connect with mongosh and insert your first document.",
        [
            section(
                "Documents and collections",
                "A **document** is a set of field-value pairs, stored as BSON (binary JSON, which adds types such as dates, ObjectId and Decimal128). Documents live in **collections**, and collections live in **databases**. Unlike rows in a SQL table, documents in one collection can have different fields, and values can be arrays or nested documents. Every document has a unique `_id`; by default it's an ObjectId, a 12-byte value that starts with its creation time.",
                r'''
                {
                  _id: ObjectId("665f1c2e8a1b2c3d4e5f6a7b"),
                  name: "Ada Lovelace",
                  email: "ada@example.com",
                  skills: ["python", "sql"],
                  address: { city: "London", country: "UK" },
                  joinedAt: ISODate("2026-01-15T09:30:00Z")
                }
                ''',
                "mongosh",
            ),
            section(
                "Run MongoDB and connect",
                "The quickest way to run MongoDB locally is Docker, which you learned in the Docker course. `mongosh` is the MongoDB shell and uses JavaScript syntax. `use learning` switches to a database; MongoDB creates databases and collections the first time you write to them.",
                r'''
                # In a terminal
                docker run -d --name mongo -p 27017:27017 -v mongodata:/data/db mongo:8.0
                docker exec -it mongo mongosh

                # Inside mongosh
                use learning
                db.students.insertOne({ name: "Ada Lovelace", skills: ["python", "sql"] })
                db.students.find()
                show collections
                ''',
                "shell",
            ),
            section(
                "When to choose MongoDB",
                "MongoDB fits data that is naturally document-shaped and read together (product catalogs, user profiles, content, events), schemas that change often, and very large datasets that need built-in horizontal scaling. PostgreSQL fits highly relational data, complex joins and reporting, and strict rules enforced across many rows. Both are mature: MongoDB has multi-document transactions and PostgreSQL has JSONB, so choose by access patterns, not feature lists.",
            ),
        ],
        [
            "Documents are BSON field-value pairs; collections group documents; `_id` is unique.",
            "Documents can nest objects and arrays, and fields can differ between documents.",
            "Databases and collections are created on the first write.",
            "Choose MongoDB for document-shaped data that's read together, and SQL for heavily relational data.",
        ],
        r'''
        // Terminal: docker run -d --name mongo -p 27017:27017 mongo:8.0
        // Then:     docker exec -it mongo mongosh
        use learning
        db.students.insertOne({
          name: "Ada Lovelace",
          email: "ada@example.com",
          skills: ["python", "sql"],
          address: { city: "London" },
          joinedAt: new Date()
        })
        // { acknowledged: true, insertedId: ObjectId("...") }

        db.students.findOne({ name: "Ada Lovelace" })
        db.students.countDocuments()          // 1
        show dbs                              // "learning" now exists
        ''',
        [
            question("How does MongoDB store documents?", ["As CSV", "As BSON", "As XML", "As plain text"], 1,
                     "BSON is a binary form of JSON with extra types such as dates and ObjectId."),
            question("When is a collection created?",
                     ["Only with createCollection()", "Automatically on the first insert", "When the server starts", "Never: you must use SQL"], 1,
                     "You can call createCollection() for options such as validation, but a plain insert creates it too."),
            question("Which is a good fit for MongoDB?",
                     ["A ledger with complex multi-table reports", "A product catalog where each product has different attributes",
                      "Data that must be joined across ten tables in every query", "None of these"], 1,
                     "Varied attributes that are read together as one item suit the document model."),
        ],
        "mongosh",
    ),
    "mongo-crud": lesson(
        "Create, read, update and delete are the everyday MongoDB operations. Filters are documents too, and update operators change fields in place.",
        [
            section(
                "Insert and find",
                "`insertOne` and `insertMany` add documents. `find(filter, projection)` returns a cursor over the matching documents, and `findOne` returns the first match. A filter is a document: `{ city: \"London\" }` means city equals London. A projection chooses fields: `{ name: 1, _id: 0 }` returns only the name.",
                r'''
                db.students.insertMany([
                  { name: "Ada", city: "London", score: 91, courses: ["python"] },
                  { name: "Grace", city: "New York", score: 88, courses: ["python", "sql"] },
                  { name: "Alan", city: "London", score: 75, courses: [] }
                ])

                db.students.find({ city: "London" }, { name: 1, score: 1, _id: 0 })
                // [ { name: "Ada", score: 91 }, { name: "Alan", score: 75 } ]

                db.students.findOne({ name: "Grace" })
                db.students.countDocuments({ city: "London" })   // 2
                ''',
                "mongosh",
            ),
            section(
                "Update with operators",
                "Updates take a filter and an update document made of operators: `$set` sets fields, `$unset` removes them, `$inc` adds to a number, `$push` appends to an array and `$addToSet` appends only if the value is missing. `replaceOne` swaps the whole document instead. With `upsert: true`, MongoDB inserts a document when nothing matches. Every write to a single document is atomic.",
                r'''
                db.students.updateOne({ name: "Alan" }, { $set: { city: "Manchester" }, $inc: { score: 5 } })
                db.students.updateOne({ name: "Alan" }, { $addToSet: { courses: "dsa" } })
                db.students.updateMany({}, { $set: { active: true } })

                db.students.updateOne(
                  { email: "linus@example.com" },
                  { $set: { name: "Linus", score: 0 } },
                  { upsert: true }
                )   // inserts a new document, because no document matched
                ''',
                "mongosh",
            ),
            section(
                "Delete",
                "`deleteOne` removes the first match and `deleteMany` removes every match. `deleteMany({})` empties the whole collection, so run the same filter with `find` first and check what it returns.",
                r'''
                db.students.find({ active: false })        // check first
                db.students.deleteMany({ active: false })
                db.students.deleteOne({ name: "Linus" })
                ''',
                "mongosh",
            ),
        ],
        [
            "Filters and projections are documents: `{ field: value }` matches equality.",
            "Use update operators ($set, $inc, $push, $addToSet) rather than rewriting whole documents.",
            "`upsert: true` inserts a document when none matches.",
            "Writes to a single document are atomic; check delete filters with find first.",
        ],
        r'''
        use learning
        db.students.drop()
        db.students.insertMany([
          { name: "Ada", city: "London", score: 91, courses: ["python"] },
          { name: "Grace", city: "New York", score: 88, courses: ["python", "sql"] },
          { name: "Alan", city: "London", score: 75, courses: [] },
          { name: "Edsger", city: "Austin", score: 64, courses: ["dsa"] }
        ])

        db.students.find({ city: "London" }, { name: 1, score: 1, _id: 0 })
        db.students.updateOne({ name: "Alan" }, { $set: { city: "Manchester" }, $inc: { score: 10 } })
        db.students.updateOne({ name: "Ada" }, { $addToSet: { courses: "dsa" } })
        db.students.updateOne({ name: "Ada" }, { $addToSet: { courses: "dsa" } })   // no duplicate is added
        db.students.findOne({ name: "Ada" }).courses                                 // [ "python", "dsa" ]

        db.students.find({ score: { $lt: 70 } })      // Edsger: check before deleting
        db.students.deleteOne({ name: "Edsger" })
        db.students.countDocuments()                  // 3
        ''',
        [
            question("Which update adds 5 to a score without reading it first?",
                     ["{ score: score + 5 }", "{ $inc: { score: 5 } }", "{ $set: { score: 5 } }", "{ $push: { score: 5 } }"], 1,
                     "$inc changes the value on the server, atomically. $set would overwrite it with 5."),
            question("What does $addToSet do?",
                     ["Always appends", "Appends only if the value isn't already in the array", "Creates a set collection", "Removes duplicates from all arrays"], 1,
                     "It treats the array like a set, which makes repeated calls safe."),
            question("What does { upsert: true } do when no document matches?",
                     ["Nothing", "Throws an error", "Inserts a new document built from the filter and the update", "Updates every document"], 2,
                     "Upserts are handy for 'create or update' operations such as counters and settings."),
        ],
        "mongosh",
    ),
    "mongo-queries": lesson(
        "Query operators let you filter by ranges, lists, arrays and nested fields, then sort, limit and shape the results.",
        [
            section(
                "Comparison and logical operators",
                "Operators start with `$`: `$gt`, `$gte`, `$lt`, `$lte`, `$ne`, `$in` and `$nin` compare values, and `$and`, `$or` and `$not` combine conditions. Conditions listed together in one filter are already combined with AND. `$exists` checks whether a field is present, and `$regex` matches patterns (anchor it with `^` so it can use an index).",
                r'''
                db.students.find({ score: { $gte: 80, $lt: 95 } })
                db.students.find({ city: { $in: ["London", "Paris"] } })
                db.students.find({ $or: [{ score: { $gte: 90 } }, { courses: "dsa" }] })
                db.students.find({ phone: { $exists: false } })
                db.students.find({ name: { $regex: "^Gr" } })
                ''',
                "mongosh",
            ),
            section(
                "Nested documents and arrays",
                "Reach into embedded documents with dot notation, written in quotes: `\"instructor.country\"`. A plain value matched against an array field matches if any element equals it. `$all` requires every listed value, `$size` matches the array length, and `$elemMatch` requires a single element to meet several conditions at once.",
                r'''
                db.courses.insertOne({
                  title: "PostgreSQL and SQL",
                  tags: ["database", "sql"],
                  instructor: { name: "Grace", country: "US" },
                  reviews: [{ user: "ada", stars: 5 }, { user: "alan", stars: 3 }]
                })

                db.courses.find({ "instructor.country": "US" })
                db.courses.find({ tags: "sql" })                                  // any element equals "sql"
                db.courses.find({ tags: { $all: ["sql", "database"] } })
                db.courses.find({ reviews: { $elemMatch: { user: "ada", stars: { $gte: 4 } } } })
                ''',
                "mongosh",
            ),
            section(
                "Sort, limit, skip and projection",
                "Chain `sort`, `skip` and `limit` on a cursor: `1` sorts ascending and `-1` descending. Like OFFSET in SQL, a large `skip` gets slow, so page with a range filter on an indexed field instead (`{ _id: { $gt: lastId } }`). Project only the fields you need, to save bandwidth.",
                r'''
                db.students.find({}, { name: 1, score: 1 }).sort({ score: -1 }).limit(3)    // top three

                // Next page: everything after the last _id the client saw
                db.students.find({ _id: { $gt: ObjectId("665f1c2e8a1b2c3d4e5f6a7b") } }).sort({ _id: 1 }).limit(20)
                ''',
                "mongosh",
            ),
        ],
        [
            "Operators such as $gt, $in and $or build filters; conditions in one filter are ANDed.",
            "Use dot notation for nested fields, and $elemMatch when one array element must meet several conditions.",
            "A value matched against an array field matches if any element equals it.",
            "Page with range filters on indexed fields rather than large skip values.",
        ],
        r'''
        use learning
        db.courses.drop()
        db.courses.insertMany([
          { title: "Python Foundations", price: 0, tags: ["python"],
            instructor: { name: "Ada", country: "UK" }, reviews: [{ user: "sam", stars: 5 }] },
          { title: "PostgreSQL and SQL", price: 49, tags: ["database", "sql"],
            instructor: { name: "Grace", country: "US" }, reviews: [{ user: "ada", stars: 5 }, { user: "alan", stars: 3 }] },
          { title: "MongoDB and NoSQL", price: 39, tags: ["database", "nosql"],
            instructor: { name: "Linus", country: "FI" }, reviews: [{ user: "ada", stars: 2 }, { user: "sam", stars: 5 }] }
        ])

        // Paid database courses, cheapest first, showing only title and price
        db.courses.find({ tags: "database", price: { $gt: 0 } }, { title: 1, price: 1, _id: 0 }).sort({ price: 1 })
        // MongoDB and NoSQL (39), then PostgreSQL and SQL (49)

        // Courses taught by instructors outside the US
        db.courses.find({ "instructor.country": { $ne: "US" } }, { title: 1, _id: 0 })

        // Courses where Ada left a review of 4 stars or more
        db.courses.find({ reviews: { $elemMatch: { user: "ada", stars: { $gte: 4 } } } }, { title: 1, _id: 0 })
        // Only "PostgreSQL and SQL". Without $elemMatch, MongoDB would match too:
        // Ada reviewed it (2 stars) and someone else gave it 5.
        ''',
        [
            question("How do you query the city field inside an embedded address document?",
                     ["{ address: { city: \"London\" } }", "{ \"address.city\": \"London\" }", "{ address->city: \"London\" }", "{ $nested: \"London\" }"], 1,
                     "Dot notation matches the nested field. `{ address: { city: \"London\" } }` only matches if address is exactly { city: \"London\" }, with no other fields."),
            question("What does { tags: \"sql\" } match when tags is an array?",
                     ["Only arrays equal to [\"sql\"]", "Documents where any element of tags is \"sql\"", "Nothing", "It's a syntax error"], 1,
                     "Equality on an array field checks each element."),
            question("Why use $elemMatch?",
                     ["To sort arrays", "So that one array element must satisfy all the conditions together", "To count elements", "To create indexes"], 1,
                     "Without it, each condition can be met by a different element, which gives surprising matches."),
        ],
        "mongosh",
    ),
    "mongo-modeling": lesson(
        "Data modelling in MongoDB starts from how the application reads data. Embed what you read together; reference what's shared or grows without limit.",
        [
            section(
                "Embed or reference",
                "**Embed** related data inside a document when it's read together, belongs to one parent and stays bounded: an order's line items, or a user's addresses. One read returns everything, and updates are atomic. **Reference** (store an ID, then look it up separately or with `$lookup`) when the related data is large, shared by many parents, changes independently or grows without limit: a post's thousands of comments, or authors shared across posts.\n\nRules of thumb: one-to-few, embed; one-to-many, embed or reference; one-to-squillions, reference from the child.",
                r'''
                // Embedded: an order and its items come back in one read
                db.orders.insertOne({
                  _id: 5001,
                  customerId: 42,
                  status: "paid",
                  items: [
                    { sku: "BOOK-1", title: "Dune", qty: 1, price: 9.99 },
                    { sku: "PEN-3", title: "Gel pen", qty: 3, price: 1.5 }
                  ],
                  shipping: { city: "London", postcode: "N1 9GU" }
                })

                // Referenced: comments point to their post, so a post never grows without limit
                db.comments.insertOne({ postId: 77, author: "ada", text: "Great post!", at: new Date() })
                db.comments.createIndex({ postId: 1, at: -1 })
                ''',
                "mongosh",
            ),
            section(
                "Limits, duplication and validation",
                "A document can be at most 16 MB, and arrays that grow forever make documents slow to read and update, so cap them or move the items to their own collection. Some duplication is normal: storing the product title and price in each order item keeps the order correct even if the product changes later. Add a `$jsonSchema` validator to enforce required fields and types on every write.",
                r'''
                db.createCollection("products", {
                  validator: {
                    $jsonSchema: {
                      bsonType: "object",
                      required: ["name", "price", "sku"],
                      properties: {
                        name: { bsonType: "string", minLength: 1 },
                        price: { bsonType: ["double", "decimal", "int"], minimum: 0 },
                        sku: { bsonType: "string" }
                      }
                    }
                  }
                })
                db.products.insertOne({ name: "Mug" })   // fails validation: price and sku are missing
                ''',
                "mongosh",
            ),
        ],
        [
            "Model for your read patterns: embed what is read together and bounded.",
            "Reference data that is shared, large or grows without limit.",
            "Documents max out at 16 MB, so avoid unbounded arrays.",
            "Some duplication is fine; enforce structure with $jsonSchema validators.",
        ],
        r'''
        // Blog schema, designed for the main page: "show a post with its author and latest comments".

        // authors: shared by many posts, so they get their own collection
        db.authors.insertOne({ _id: "ada", name: "Ada Lovelace", bio: "Mathematician" })

        // posts: a reference to the author plus a cached copy of the name (no lookup to show it),
        // tags embedded (one-to-few), and only the 3 newest comments embedded (subset pattern)
        db.posts.insertOne({
          _id: 77,
          title: "Embedding vs referencing",
          body: "...",
          author: { id: "ada", name: "Ada Lovelace" },
          tags: ["mongodb", "modeling"],
          commentCount: 1,
          latestComments: [{ author: "alan", text: "Clear!", at: new Date() }]
        })

        // comments: one-to-squillions, so each comment references its post
        db.comments.insertOne({ postId: 77, author: "alan", text: "Clear!", at: new Date() })
        db.comments.createIndex({ postId: 1, at: -1 })

        // Adding a comment: insert it, then update the counter and the capped preview list
        db.comments.insertOne({ postId: 77, author: "grace", text: "Nice", at: new Date() })
        db.posts.updateOne({ _id: 77 }, {
          $inc: { commentCount: 1 },
          $push: { latestComments: { $each: [{ author: "grace", text: "Nice", at: new Date() }], $position: 0, $slice: 3 } }
        })
        ''',
        [
            question("An order has a handful of line items that are always shown with it. How should you store them?",
                     ["In a separate collection", "Embedded in the order document", "In GridFS", "In a separate database"], 1,
                     "They're few, owned by the order and read with it: the textbook case for embedding."),
            question("Why shouldn't a post embed all of its comments?",
                     ["Comments can't be embedded", "Comments can grow without limit, making the document huge and pushing it toward the 16 MB limit",
                      "Embedding is slower to read", "MongoDB forbids arrays of objects"], 1,
                     "Unbounded arrays are the most common MongoDB modelling mistake."),
            question("What is the maximum size of a MongoDB document?", ["1 MB", "16 MB", "100 MB", "Unlimited"], 1,
                     "Large files belong in object storage or GridFS, not inside documents."),
        ],
        "mongosh",
    ),
    "mongo-indexes": lesson(
        "Indexes let MongoDB find documents without scanning the whole collection. Learn the index types, the field-order rule for compound indexes, and how to read explain().",
        [
            section(
                "Create indexes",
                "Without an index, a query is a **collection scan** (COLLSCAN): MongoDB reads every document. An index is a sorted structure (a B-tree) on one or more fields that lets it jump straight to the matches (IXSCAN). Index types include single-field, compound (several fields), multikey (on arrays, created automatically), unique, TTL (deletes documents after a set time), partial (indexes only some documents) and text. `_id` is always indexed.",
                r'''
                db.students.createIndex({ email: 1 }, { unique: true })
                db.students.createIndex({ city: 1, score: -1 })                           // compound
                db.sessions.createIndex({ createdAt: 1 }, { expireAfterSeconds: 3600 })   // TTL: removed after an hour
                db.orders.createIndex({ customerId: 1 }, { partialFilterExpression: { status: "open" } })
                db.students.getIndexes()
                ''',
                "mongosh",
            ),
            section(
                "Compound indexes and the ESR rule",
                "Field order in a compound index matters. Follow the **ESR rule**: fields matched by **E**quality first, then fields you **S**ort on, then **R**ange filters. An index on `{ a: 1, b: 1 }` also serves queries on `a` alone (a prefix of the index) but not on `b` alone. A **covered query** asks only for indexed fields, so MongoDB answers it from the index without reading any documents.",
                r'''
                // Query: students in London with a score above 70, sorted by name
                db.students.find({ city: "London", score: { $gt: 70 } }).sort({ name: 1 })

                // ESR: equality (city), then sort (name), then range (score)
                db.students.createIndex({ city: 1, name: 1, score: 1 })
                ''',
                "mongosh",
            ),
            section(
                "Read explain()",
                "`explain(\"executionStats\")` shows the plan MongoDB chose and how much work it did. Compare `totalDocsExamined` and `totalKeysExamined` with `nReturned`: a good plan examines about as many documents as it returns. A COLLSCAN on a big collection, or a SORT stage done in memory, means you need a better index. Every index speeds up reads but slows down writes and uses memory, so drop the ones you don't use.",
                r'''
                db.students.find({ city: "London", score: { $gt: 70 } }).sort({ name: 1 }).explain("executionStats")
                // Look at: the stages in queryPlanner.winningPlan (IXSCAN or COLLSCAN, any SORT),
                //          executionStats.nReturned, totalKeysExamined, totalDocsExamined, executionTimeMillis
                ''',
                "mongosh",
            ),
        ],
        [
            "Without an index, MongoDB scans every document (COLLSCAN).",
            "Order compound index fields by Equality, Sort, Range (ESR).",
            "Use explain(\"executionStats\") and compare documents examined with documents returned.",
            "Indexes speed up reads but cost write speed and memory; remove unused ones.",
        ],
        r'''
        use learning
        db.students.drop()
        const docs = []
        for (let i = 0; i < 100000; i++) {
          docs.push({ name: "student" + i, city: ["London", "Paris", "Pune"][i % 3], score: i % 100 })
        }
        db.students.insertMany(docs)

        const query = () => db.students.find({ city: "Pune", score: { $gte: 95 } }).sort({ name: 1 })

        const before = query().explain("executionStats")
        before.executionStats.nReturned            // about 1,667 matches
        before.executionStats.totalDocsExamined    // 100000: a COLLSCAN, followed by an in-memory SORT

        db.students.createIndex({ city: 1, name: 1, score: 1 })   // ESR order

        const after = query().explain("executionStats")
        after.executionStats.totalDocsExamined     // about 1,667: only the matches are fetched
        after.executionStats.totalKeysExamined     // index keys for city "Pune", already sorted by name
        after.executionStats.executionTimeMillis   // compare with before.executionStats.executionTimeMillis
        ''',
        [
            question("In explain() output, which stage means MongoDB read every document?", ["IXSCAN", "COLLSCAN", "FETCH", "PROJECTION"], 1,
                     "IXSCAN walks an index; COLLSCAN reads the whole collection."),
            question("A query filters on status, sorts by createdAt and has a range on total. Which index follows ESR?",
                     ["{ total: 1, status: 1, createdAt: 1 }", "{ status: 1, createdAt: 1, total: 1 }", "{ createdAt: 1, total: 1, status: 1 }", "{ total: 1 }"], 1,
                     "Equality (status), then sort (createdAt), then range (total)."),
            question("What does a TTL index do?",
                     ["Speeds up text search", "Deletes documents automatically after a set time", "Makes values unique", "Compresses data"], 1,
                     "TTL indexes are ideal for sessions, password-reset tokens and temporary data."),
        ],
        "mongosh",
    ),
    "mongo-aggregation": lesson(
        "The aggregation pipeline transforms documents through a series of stages, like a Unix pipe: filter, group, reshape, join and sort, all inside the database.",
        [
            section(
                "Stages: $match, $group, $sort and $project",
                "A pipeline is an array of stages, and each stage passes its output to the next. `$match` filters (put it first, so it can use indexes). `$group` groups by a key and computes accumulators such as `$sum`, `$avg`, `$max` and `$push`. `$sort` orders, `$limit` trims, and `$project` or `$set` reshape documents. Together they do the job of SQL's WHERE, GROUP BY and SELECT.",
                r'''
                db.enrolments.insertMany([
                  { student: "Ada", course: "python", score: 91 },
                  { student: "Grace", course: "python", score: 88 },
                  { student: "Alan", course: "sql", score: 75 },
                  { student: "Ada", course: "sql", score: 84 }
                ])

                db.enrolments.aggregate([
                  { $match: { score: { $gte: 50 } } },
                  { $group: { _id: "$course", avgScore: { $avg: "$score" }, students: { $sum: 1 } } },
                  { $sort: { avgScore: -1 } },
                  { $project: { _id: 0, course: "$_id", avgScore: { $round: ["$avgScore", 1] }, students: 1 } }
                ])
                // python: avgScore 89.5 with 2 students; sql: avgScore 79.5 with 2 students
                ''',
                "mongosh",
            ),
            section(
                "$unwind and $lookup",
                "`$unwind` turns an array into one document per element, so you can group by array values. `$lookup` performs a left outer join with another collection. Joins are possible, but if every request needs a `$lookup`, consider embedding the data instead.",
                r'''
                // The most common tags across courses
                db.courses.aggregate([
                  { $unwind: "$tags" },
                  { $group: { _id: "$tags", count: { $sum: 1 } } },
                  { $sort: { count: -1 } }
                ])

                // Join each enrolment with the student's profile
                db.enrolments.aggregate([
                  { $lookup: { from: "students", localField: "student", foreignField: "name", as: "profile" } },
                  { $unwind: "$profile" },
                  { $project: { _id: 0, student: 1, course: 1, city: "$profile.city" } }
                ])
                ''',
                "mongosh",
            ),
        ],
        [
            "A pipeline is an ordered list of stages; each stage feeds the next.",
            "Put $match (and $sort with $limit) early, so indexes are used and less data flows through.",
            "$group with accumulators replaces SQL's GROUP BY; $unwind flattens arrays.",
            "$lookup joins collections, but frequent joins suggest the data should be embedded.",
        ],
        r'''
        use learning
        db.enrolments.drop()
        db.enrolments.insertMany([
          { student: "Ada", course: "python", score: 91 },
          { student: "Grace", course: "python", score: 88 },
          { student: "Alan", course: "python", score: 62 },
          { student: "Linus", course: "python", score: 95 },
          { student: "Ada", course: "sql", score: 84 },
          { student: "Alan", course: "sql", score: 75 }
        ])

        db.enrolments.aggregate([
          { $group: {
              _id: "$course",
              avgScore: { $avg: "$score" },
              topThree: { $topN: { n: 3, sortBy: { score: -1 }, output: { student: "$student", score: "$score" } } }
          } },
          { $project: { _id: 0, course: "$_id", avgScore: { $round: ["$avgScore", 1] }, topThree: 1 } },
          { $sort: { course: 1 } }
        ])
        // python: avgScore 84, topThree Linus 95, Ada 91, Grace 88
        // sql:    avgScore 79.5, topThree Ada 84, Alan 75
        ''',
        [
            question("Why put $match at the start of a pipeline?",
                     ["It's required", "It can use indexes and reduces the documents that later stages process", "It sorts the results", "It enables $lookup"], 1,
                     "Filtering first means every later stage does less work."),
            question("What does $unwind do?", ["Removes arrays", "Outputs one document per array element", "Joins collections", "Sorts arrays"], 1,
                     "A document with a 3-element array becomes 3 documents, one per element."),
            question("Which stage is closest to SQL's GROUP BY?", ["$match", "$project", "$group", "$lookup"], 2,
                     "$match is like WHERE, $project like SELECT and $lookup like a LEFT JOIN."),
        ],
        "mongosh",
    ),
    "mongo-python": lesson(
        "PyMongo is MongoDB's official Python driver. Connect once, reuse the client, and wrap database access in a small repository class that the rest of your application calls.",
        [
            section(
                "Connect and run CRUD",
                "Install it with `pip install pymongo`. Create one `MongoClient` per process and reuse it: it holds a connection pool and is thread-safe. Read the connection string from an environment variable. Documents are Python dicts, and `_id` values are `ObjectId` objects, which you convert to and from strings at your API boundary.",
                r'''
                import os

                from bson import ObjectId
                from pymongo import MongoClient

                client = MongoClient(os.environ.get("MONGODB_URI", "mongodb://localhost:27017"), serverSelectionTimeoutMS=3000)
                students = client["learning"]["students"]

                result = students.insert_one({"name": "Ada", "city": "London", "score": 91})
                print(result.inserted_id)                                # ObjectId('...')

                for doc in students.find({"city": "London"}, {"name": 1, "score": 1}).sort("score", -1).limit(5):
                    print(doc["name"], doc["score"])

                students.update_one({"_id": result.inserted_id}, {"$inc": {"score": 2}})
                student_id = str(result.inserted_id)                     # what an API would return
                print(students.find_one({"_id": ObjectId(student_id)}))  # and how it looks it up again
                ''',
            ),
            section(
                "Async apps, indexes and errors",
                "For async frameworks such as FastAPI, use PyMongo's async API, `AsyncMongoClient`, which replaces the older Motor library: the calls are the same, with `await`. Create indexes at startup with `create_index` (it does nothing if the index already exists). Catch `DuplicateKeyError` for unique violations rather than checking first, because a check-then-insert can race.",
                r'''
                from contextlib import asynccontextmanager

                from fastapi import FastAPI, HTTPException
                from pydantic import BaseModel
                from pymongo import AsyncMongoClient
                from pymongo.errors import DuplicateKeyError

                client = AsyncMongoClient("mongodb://localhost:27017")
                students = client["learning"]["students"]


                @asynccontextmanager
                async def lifespan(app: FastAPI):
                    await students.create_index("email", unique=True)
                    yield
                    await client.close()


                app = FastAPI(lifespan=lifespan)


                class StudentIn(BaseModel):
                    name: str
                    email: str


                @app.post("/students", status_code=201)
                async def create_student(student: StudentIn):
                    try:
                        result = await students.insert_one(student.model_dump())
                    except DuplicateKeyError:
                        raise HTTPException(409, "Email already registered") from None
                    return {"id": str(result.inserted_id)}
                ''',
            ),
        ],
        [
            "Create one MongoClient per process and reuse it; it manages a connection pool.",
            "Convert ObjectId to a string at the API boundary, and back with ObjectId(id).",
            "Rely on unique indexes and catch DuplicateKeyError instead of check-then-insert.",
            "Use AsyncMongoClient in async frameworks such as FastAPI.",
        ],
        r'''
        import os
        import re

        from bson import ObjectId
        from bson.errors import InvalidId
        from pymongo import ASCENDING, DESCENDING, MongoClient
        from pymongo.collection import Collection
        from pymongo.errors import DuplicateKeyError


        class StudentRepository:
            def __init__(self, collection: Collection):
                self.students = collection
                self.students.create_index([("email", ASCENDING)], unique=True)
                self.students.create_index([("city", ASCENDING), ("score", DESCENDING)])

            def create(self, name: str, email: str, city: str, score: int = 0) -> str:
                document = {"name": name, "email": email.lower(), "city": city, "score": score}
                try:
                    result = self.students.insert_one(document)
                except DuplicateKeyError:
                    raise ValueError(f"{email} is already registered") from None
                return str(result.inserted_id)

            def get(self, student_id: str) -> dict | None:
                try:
                    doc = self.students.find_one({"_id": ObjectId(student_id)})
                except InvalidId:
                    return None                     # a malformed id is simply "not found"
                return self._to_api(doc) if doc else None

            def search(self, city: str | None = None, min_score: int = 0, name_prefix: str = "", limit: int = 20) -> list[dict]:
                query: dict = {"score": {"$gte": min_score}}
                if city:
                    query["city"] = city
                if name_prefix:
                    query["name"] = {"$regex": "^" + re.escape(name_prefix)}   # escaped: no regex injection
                cursor = self.students.find(query).sort("score", DESCENDING).limit(min(limit, 100))
                return [self._to_api(doc) for doc in cursor]

            @staticmethod
            def _to_api(doc: dict) -> dict:
                doc["id"] = str(doc.pop("_id"))
                return doc


        if __name__ == "__main__":
            client = MongoClient(os.environ.get("MONGODB_URI", "mongodb://localhost:27017"))
            collection = client["learning"]["repo_demo"]
            collection.drop()                       # start the demo from an empty collection
            repo = StudentRepository(collection)

            ada_id = repo.create("Ada", "ada@example.com", "London", 91)
            repo.create("Alan", "alan@example.com", "London", 75)
            print(repo.get(ada_id))                              # Ada's document, with a string id
            print(repo.search(city="London", min_score=80))      # only Ada
            print(repo.get("not-an-id"))                         # None, not a crash
            try:
                repo.create("Ada again", "ADA@example.com", "Paris")
            except ValueError as error:
                print(error)                                     # already registered
            client.close()
        ''',
        [
            question("How many MongoClient instances should a web app create?",
                     ["One per request", "One per process, reused", "One per query", "One per collection"], 1,
                     "Each client owns a connection pool; creating one per request exhausts server connections."),
            question("How do you look up a document by an id string taken from a URL?",
                     ["find_one({\"_id\": id})", "find_one({\"_id\": ObjectId(id)})", "find_by_id(id)", "find_one(id)"], 1,
                     "A string never equals an ObjectId, so convert it first, and handle InvalidId for malformed input."),
            question("Why catch DuplicateKeyError instead of checking whether the email exists first?",
                     ["It's shorter to type", "Check-then-insert races: two requests can both pass the check, so the unique index is the real guard",
                      "find_one is deprecated", "Exceptions are free"], 1,
                     "Only the database can enforce uniqueness reliably under concurrency."),
        ],
    ),
    "mongo-transactions": lesson(
        "Writes to a single document are always atomic. When a change must update several documents together, use a transaction, and choose write and read settings that match how safe and fresh the data must be.",
        [
            section(
                "Multi-document transactions",
                "Transactions make several operations all-or-nothing, with snapshot isolation; they need a replica set or a sharded cluster. In PyMongo, `session.with_transaction(callback)` starts the transaction, commits it, and retries automatically on temporary errors, so the callback must be safe to run more than once. Keep transactions short (60 seconds is the default limit), and prefer a document model where most changes touch one document.\n\nTo try this locally, start a single-node replica set: `docker run -d --name mongo-rs -p 27017:27017 mongo:8.0 --replSet rs0`, then run `rs.initiate({_id: \"rs0\", members: [{_id: 0, host: \"localhost:27017\"}]})` in mongosh.",
                r'''
                from pymongo import MongoClient

                client = MongoClient("mongodb://localhost:27017/?replicaSet=rs0")
                accounts = client["bank"]["accounts"]


                def transfer(session, source: str, target: str, amount: int) -> None:
                    debited = accounts.update_one(
                        {"_id": source, "balance": {"$gte": amount}}, {"$inc": {"balance": -amount}}, session=session
                    )
                    if debited.modified_count != 1:
                        raise ValueError("insufficient funds")      # aborts the whole transaction
                    accounts.update_one({"_id": target}, {"$inc": {"balance": amount}}, session=session)


                with client.start_session() as session:
                    session.with_transaction(lambda s: transfer(s, "alice", "bob", 30))
                ''',
            ),
            section(
                "Write concern, read concern and read preference",
                "**Write concern** sets how many replica-set members must confirm a write: `w=1` (the primary only, fast) or `w=\"majority\"` (survives a primary failover; the default since MongoDB 5.0). `j=True` also waits for the on-disk journal. **Read concern** sets which data a read may see: `local` (the node's latest data, which could still be rolled back) or `majority` (only data confirmed by a majority). **Read preference** chooses which members serve reads: `primary` (the default and freshest) or secondaries (spreads the load, but may be slightly stale).",
                r'''
                from pymongo import MongoClient, ReadPreference
                from pymongo.read_concern import ReadConcern
                from pymongo.write_concern import WriteConcern

                client = MongoClient("mongodb://localhost:27017/?replicaSet=rs0")
                db = client["shop"]

                orders = db.get_collection("orders", write_concern=WriteConcern(w="majority", j=True))
                reports = db.get_collection(
                    "orders", read_preference=ReadPreference.SECONDARY_PREFERRED, read_concern=ReadConcern("majority")
                )
                ''',
            ),
        ],
        [
            "Single-document writes are atomic; transactions make multi-document changes all-or-nothing.",
            "Transactions need a replica set or sharded cluster; keep them short and safe to retry.",
            "w=\"majority\" writes survive a primary failover; w=1 is faster but can be rolled back.",
            "Reading from secondaries spreads load but may return slightly stale data.",
        ],
        r'''
        # Transactions need a replica set. Start a single-node one first:
        #   docker run -d --name mongo-rs -p 27017:27017 mongo:8.0 --replSet rs0
        #   docker exec -it mongo-rs mongosh --eval 'rs.initiate({_id: "rs0", members: [{_id: 0, host: "localhost:27017"}]})'
        from pymongo import MongoClient
        from pymongo.write_concern import WriteConcern

        client = MongoClient("mongodb://localhost:27017/?replicaSet=rs0")
        accounts = client["bank"].get_collection("accounts", write_concern=WriteConcern(w="majority"))
        accounts.drop()
        accounts.insert_many([{"_id": "alice", "balance": 100}, {"_id": "bob", "balance": 20}])


        class InsufficientFunds(Exception):
            pass


        def transfer(source: str, target: str, amount: int) -> None:
            def work(session) -> None:
                debited = accounts.update_one(
                    {"_id": source, "balance": {"$gte": amount}}, {"$inc": {"balance": -amount}}, session=session
                )
                if debited.modified_count != 1:
                    raise InsufficientFunds(f"{source} can't send {amount}")
                credited = accounts.update_one({"_id": target}, {"$inc": {"balance": amount}}, session=session)
                if credited.matched_count != 1:
                    raise ValueError(f"unknown account {target}")

            with client.start_session() as session:
                session.with_transaction(work)


        transfer("alice", "bob", 30)
        for source, target, amount in [("alice", "bob", 500), ("alice", "nobody", 10)]:
            try:
                transfer(source, target, amount)
            except (InsufficientFunds, ValueError) as error:
                print("rolled back:", error)

        print(list(accounts.find()))          # alice 70, bob 50: the failed transfers changed nothing
        assert sum(doc["balance"] for doc in accounts.find()) == 120
        ''',
        [
            question("Which operations are atomic without a transaction?",
                     ["Any updateMany", "Writes to a single document", "Nothing", "All the writes in one HTTP request"], 1,
                     "updateMany is atomic per document, not as a whole."),
            question("What does write concern w=\"majority\" guarantee?",
                     ["The write is on every node", "A majority of replica-set members confirmed it, so it survives a primary failover", "The write is encrypted", "The write is cached"], 1,
                     "Writes confirmed only by the primary (w=1) can be rolled back if it fails before replicating them."),
            question("Why must a with_transaction callback be safe to run more than once?",
                     ["It always runs twice", "The driver retries it on temporary errors", "Python requires it", "To make it faster"], 1,
                     "On a transient error the driver runs the whole callback again, so it mustn't have side effects outside the transaction."),
        ],
    ),
    "mongo-scale": lesson(
        "Replica sets keep MongoDB available when a server fails, and sharding spreads data across machines when one server isn't enough. Choosing the shard key is the most important scaling decision.",
        [
            section(
                "Replica sets",
                "A **replica set** is a group of servers, usually three, holding the same data. One **primary** accepts all writes and records them in its oplog; **secondaries** copy the oplog and apply it. If the primary fails, the members hold an election and a secondary becomes primary within seconds, and drivers reconnect automatically. Use an odd number of voting members, spread across failure zones, so a majority can always be formed.",
                r'''
                rs.initiate({
                  _id: "rs0",
                  members: [
                    { _id: 0, host: "mongo1:27017" },
                    { _id: 1, host: "mongo2:27017" },
                    { _id: 2, host: "mongo3:27017" }
                  ]
                })
                rs.status()          // shows the PRIMARY and SECONDARY members and their replication lag
                ''',
                "mongosh",
            ),
            section(
                "Sharding and shard keys",
                "**Sharding** splits a collection across several replica sets (shards) by a **shard key**, and a router (`mongos`) sends each query to the right shards. A good shard key has many distinct values, spreads writes evenly and appears in most queries, so they go to a single shard. A **ranged** key keeps nearby values together, which suits range queries, but a key that always increases, such as a timestamp, sends every insert to one 'hot' shard. A **hashed** key spreads writes evenly but turns range queries into scatter-gather. Compound keys such as `{ customerId: 1, orderDate: 1 }` often balance both.",
                r'''
                sh.enableSharding("shop")
                sh.shardCollection("shop.orders", { customerId: "hashed" })

                // Targeted: includes the shard key, so mongos asks one shard
                db.orders.find({ customerId: 42 })
                // Scatter-gather: no shard key, so every shard is queried
                db.orders.find({ status: "open" })
                ''',
                "mongosh",
            ),
            section(
                "Production checklist",
                "Enable authentication with role-based users (never expose an open database to the internet), use TLS, and restrict network access. Take regular backups and test restoring them: `mongodump` and `mongorestore` for small databases, snapshots or managed backups for large ones. Monitor replication lag, slow queries, connections, cache use and disk space. Managed services such as MongoDB Atlas handle much of this for you.",
                r'''
                mongodump --uri "mongodb://backup_user@localhost:27017/shop" --out ./backups/2026-11-22
                mongorestore --uri "mongodb://admin@localhost:27017" ./backups/2026-11-22
                ''',
                "shell",
            ),
        ],
        [
            "A replica set has one primary and several secondaries; failover elects a new primary automatically.",
            "Sharding splits a collection across shards by a shard key, and mongos routes the queries.",
            "A good shard key has many values, spreads writes evenly and appears in common queries.",
            "In production: authentication, TLS, network limits, tested backups and monitoring.",
        ],
        r'''
        Collection: shop.orders (billions of orders, heavy inserts, most queries by customer)

        Common queries
          1. A customer's recent orders:  { customerId, orderDate: { $gte: ... } }, sorted by orderDate
          2. One order by id:             { _id }
          3. Admin reports by date range: run on analytics nodes, not latency-critical

        Candidates
          { orderDate: 1 }                 always increasing: every insert hits the last shard (hot shard)
          { _id: "hashed" }                even writes, but query 1 becomes scatter-gather across every shard
          { customerId: "hashed" }         even writes and query 1 hits one shard, but date ranges
                                           within a customer can't use shard-key ranges
          { customerId: 1, orderDate: 1 }  query 1 targets one shard and is range-friendly;
                                           orders from many customers spread the inserts

        Choice: { customerId: 1, orderDate: 1 }
          + many distinct values (customers x dates), so chunks can always be split
          + inserts spread across shards, because customers are spread across them
          + the most common query includes the shard key, so one shard answers it
          - query 2 by _id alone is scatter-gather: include customerId in order URLs,
            or keep a small orderId -> customerId lookup
          - a very large customer concentrates on a few chunks: monitor chunk distribution

        Production: each shard is a 3-member replica set across availability zones, writes use
        w: "majority", authentication and TLS are on, daily backups are restored in a test,
        and alerts fire on replication lag and slow queries.
        ''',
        [
            question("What happens when a replica set's primary fails?",
                     ["Data is lost", "The remaining members elect a new primary, and drivers reconnect", "Writes go to all secondaries", "The cluster shuts down"], 1,
                     "Elections usually finish within seconds; retryable writes in modern drivers hide most of the blip."),
            question("Why is a timestamp a poor ranged shard key for heavy inserts?",
                     ["Timestamps can't be indexed", "Every new document has the largest value, so all inserts go to one hot shard", "It's too random", "It's too small"], 1,
                     "Ever-increasing keys always land in the last chunk. Hash them or use a compound key."),
            question("A query doesn't include the shard key. What does mongos do?",
                     ["Rejects it", "Sends it to every shard (scatter-gather)", "Asks only the primary shard", "Caches it"], 1,
                     "Scatter-gather works, but it gets slower as you add shards, so make common queries include the shard key."),
        ],
        "text",
    ),
}

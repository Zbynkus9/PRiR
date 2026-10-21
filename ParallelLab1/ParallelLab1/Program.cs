using System;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;

namespace ParallelLab1;

class Program
{
    private static int sharedStorage = 0;

    static int obtainUnitTime = 10;
    static int unloadUnitTime = 10;
    static int transportTime = 10000;
    static int carWeightLimit = 200;
    static int sourceSize = 2000;

    private static SemaphoreSlim semaphoreVein = new SemaphoreSlim(2, 2);
    private static SemaphoreSlim semaphoreStorage = new SemaphoreSlim(1, 1);
    private static object lockVeinObject = new object();
    private static object consoleLock = new object(); // Zamek do obsługi kursora i konsoli

    static void Main(string[] args)
    {
        Console.Clear();
        Console.CursorVisible = false;

        Task[] minerTasks = new Task[5];
        for (int i = 0; i < minerTasks.Length; i++)
        {
            int minerId = i + 1;
            minerTasks[i] = Task.Run(() => AccessSharedResource(minerId));
        }

        Task displayTask = Task.Run(() => DisplayStatistics(minerTasks));

        Task.WaitAll(minerTasks);
        displayTask.Wait();

        Console.SetCursorPosition(0, minerTasks.Length + 4);
        Console.CursorVisible = true;
    }

    static void WriteAtLine(int row, string message)
    {
        lock (consoleLock)
        {
            Console.SetCursorPosition(0, row);
            Console.Write(message.PadRight(60));
        }
    }

    static void DisplayStatistics(Task[] tasks)
    {
        while (true)
        {
            WriteAtLine(0, $"Stan złoża: {sourceSize} jednostek węgla");
            WriteAtLine(1, $"Stan magazynu: {sharedStorage} jednostek węgla");

            bool allCompleted = true;
            for (int i = 0; i < tasks.Length; i++)
            {
                if (!tasks[i].IsCompleted)
                {
                    allCompleted = false;
                    break;
                }
            }

            if (allCompleted)
            {
                break;
            }

            Thread.Sleep(50);
        }

        // Końcowe odświeżenie po zakończeniu pracy wszystkich górników
        WriteAtLine(0, $"Stan złoża: {sourceSize} jednostek węgla");
        WriteAtLine(1, $"Stan magazynu: {sharedStorage} jednostek węgla");
    }

    static void AccessSharedResource(int minerId)
    {
        int minerResources = 0;
        int minerRow = minerId + 2; // Górnik 1 -> wiersz 3, Górnik 2 -> wiersz 4 itd.

        while (true)
        {
            WriteAtLine(minerRow, $"Górnik {minerId}: Czeka na wjazd do złoża...");
            semaphoreVein.Wait();

            WriteAtLine(minerRow, $"Górnik {minerId}: Wydobywa węgiel...");
            while (minerResources < carWeightLimit)
            {
                lock (lockVeinObject)
                {
                    if (sourceSize <= 0)
                    {
                        break;
                    }
                    sourceSize--;
                    minerResources++;
                }
                Thread.Sleep(obtainUnitTime);
            }
            semaphoreVein.Release();

            if (minerResources == 0)
            {
                WriteAtLine(minerRow, $"Górnik {minerId} zakończył pracę.");
                break;
            }

            WriteAtLine(minerRow, $"Górnik {minerId}: Transportuje do magazynu...");
            Thread.Sleep(transportTime);

            WriteAtLine(minerRow, $"Górnik {minerId}: Czeka przed magazynem...");
            semaphoreStorage.Wait();

            WriteAtLine(minerRow, $"Górnik {minerId}: Rozładowuje węgiel...");
            while (minerResources > 0)
            {
                Thread.Sleep(unloadUnitTime);
                minerResources--;
                sharedStorage++;
            }
            semaphoreStorage.Release();

            if (sourceSize <= 0)
            {
                WriteAtLine(minerRow, $"Górnik {minerId} zakończył pracę.");
                break;
            }

            WriteAtLine(minerRow, $"Górnik {minerId}: Wraca do kopalni...");
            Thread.Sleep(transportTime);
        }
    }
}